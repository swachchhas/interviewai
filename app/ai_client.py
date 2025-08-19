# app/ai_client.py
import re
import hashlib
import json
import os
from typing import List
from openai import OpenAI
from app.config import API_KEYS

CACHE_FILE = "app/resume_cache.json"

# Load persistent cache if available
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        _resume_cache = json.load(f)
else:
    _resume_cache = {}

_api_key_index = 0  # rotate through keys locally in this module

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
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=_next_api_key(),
    )

def _parse_questions(text: str) -> List[str]:
    lines = text.splitlines()
    cleaned = []

    for p in lines:
        p = p.strip()
        if not p:
            continue
        # remove leading numbering/bullets/markdown
        p = re.sub(r"^\s*(?:\d+\.|\*|-|\u2022|\(|\)|#+)\s*", "", p)
        p = re.sub(r"^\*\*|\*\*$", "", p)  # remove bold wrappers

        # ensure it looks like a question
        if not p.endswith("?"):
            if len(p.split()) > 3:
                p = p.rstrip(".") + "?"
            else:
                continue

        cleaned.append(p)

    # de-dupe & cap at 10
    seen, uniq = set(), []
    for q in cleaned:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            uniq.append(q)

    return uniq[:10]

def generate_questions(resume: str, role: str = "", skills: str = "", years: str = "") -> List[str]:
    """
    Generate 8–10 interview questions.
    Caches by (resume+role+skills+years) hash.
    Rotates API keys each call.
    """
    cache_key = _hash_key("|".join([resume, role, skills, years]))
    if cache_key in _resume_cache:
        return _resume_cache[cache_key]

    prompt = f"""
You are an interview question generator. Based on the following resume and details, generate 8–10 clear, concise interview questions.
Return ONLY the questions (one per line). No numbering, headings, or extra formatting.

Resume:
{resume}

Role: {role}
Skills: {skills}
Years of Experience: {years}
"""

    try:
        client = _client()
        completion = client.chat.completions.create(
            model="deepseek/deepseek-r1-0528:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=400,
            extra_headers={
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "InterViewAI",
            },
        )
        raw = completion.choices[0].message.content or ""
        questions = _parse_questions(raw)

        if not questions:
            rough = [q.strip() for q in re.split(r"[\n,]+", raw) if q.strip()]
            questions = rough[:10] if rough else ["No questions generated. Try again."]

        # --- cache locally & persist ---
        _resume_cache[cache_key] = questions
        with open(CACHE_FILE, "w") as f:
            json.dump(_resume_cache, f)

        return questions

    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg or "Rate limit exceeded" in err_msg:
            return ["Daily free request limit reached. Please try again tomorrow or add credits."]
        return [f"Error generating questions: {err_msg}"]
