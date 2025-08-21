# app/ai_client.py
import re
import hashlib
import json
import os
from typing import List
from openai import OpenAI
from app.config import API_KEYS, Config

CACHE_FILE = "app/resume_cache.json"

# Load persistent cache
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        _resume_cache = json.load(f)
else:
    _resume_cache = {}

_api_key_index = 0  # rotate API keys locally


def _hash_key(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _next_api_key() -> str:
    global _api_key_index
    if not API_KEYS:
        raise RuntimeError("No API keys configured. Set API_KEYS in .env")
    key = API_KEYS[_api_key_index % len(API_KEYS)]
    _api_key_index += 1
    return key


def _client() -> OpenAI:
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=_next_api_key())


def _parse_questions(text: str) -> List[str]:
    """
    Convert model output into a clean list of questions:
    - prefer sentences ending with '?'
    - strip numbering / bullets / markdown
    - avoid truncated questions at the end
    """
    lines = text.splitlines()
    cleaned = []

    for p in lines:
        p = p.strip()
        if not p:
            continue

        # remove leading numbering/bullets/markdown
        p = re.sub(r"^\s*(?:\d+\.|\*|-|\u2022|\(|\)|#+)\s*", "", p)
        p = re.sub(r"^\*\*|\*\*$", "", p)  # remove bold wrappers

        # skip too short fragments
        if len(p.split()) < 3:
            continue

        # avoid cut-off endings like "of", "in", "for"
        if re.search(r"\b(of|in|for|with|and|to)$", p, re.IGNORECASE):
            continue

        # ensure it ends with a question mark
        if not p.endswith("?"):
            p = p.rstrip(".") + "?"

        cleaned.append(p)

    # de-dupe & cap at 10
    seen, uniq = set(), []
    for q in cleaned:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            uniq.append(q)

    return uniq[:10] if uniq else ["No questions generated. Please try again."]



def generate_questions_with_model(
    resume: str, role: str = "", skills: str = "", years: str = "", model_name: str = None
) -> List[str]:
    """
    Generate interview questions using a specific model (or default fallback list).
    """
    cache_key = _hash_key("|".join([resume, role, skills, years, str(model_name)]))
    if cache_key in _resume_cache:
        return _resume_cache[cache_key]

    prompt = f"""
You are an interview question generator. Based on the following resume and details, generate 8–10 clear, concise interview questions.
Number them 1 to 10. Return ONLY the questions, one per line. No extra commentary.

Resume:
{resume}

Role: {role}
Skills: {skills}
Years of Experience: {years}
"""

    client = _client()
    model_to_use = model_name or Config.get_model(0)

    completion = client.chat.completions.create(
        model=model_to_use,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
        max_tokens=600,
        extra_headers={
            "HTTP-Referer": "http://localhost:5000",
            "X-Title": "InterViewAI",
        },
    )
    raw = completion.choices[0].message.content or ""
    questions = _parse_questions(raw)

    if not questions:
        # Fallback: split by common separators
        rough = [q.strip() for q in re.split(r"[\n,;]", raw) if q.strip()]
        questions = rough[:10] if rough else ["No questions generated. Try again."]

    # Cache & persist
    _resume_cache[cache_key] = questions
    with open(CACHE_FILE, "w") as f:
        json.dump(_resume_cache, f)

    return questions


def generate_questions(resume: str, role: str = "", skills: str = "", years: str = "") -> List[str]:
    """
    Tries multiple models in order until one succeeds.
    Returns list of 8–10 questions.
    """
    last_error = None
    for model_name in Config.MODELS:
        try:
            questions = generate_questions_with_model(resume, role, skills, years, model_name=model_name)
            if questions:
                return questions
        except Exception as e:
            last_error = str(e)
            continue

    # If all models fail
    if last_error:
        if "429" in last_error or "Rate limit exceeded" in last_error:
            return ["Daily free request limit reached. Please try again tomorrow or add credits."]
        return [f"Error generating questions from all models: {last_error}"]

    return ["No questions generated. Try again."]