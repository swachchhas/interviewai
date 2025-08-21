# test_ai.py
from app.ai_client import generate_questions, _resume_cache

# Clear cache for testing
_resume_cache.clear()

# Sample resume (short to avoid token issues)
sample_resume = """
John Doe
Software Engineer with 5 years experience in Python, AI, and web development.
Led several projects involving machine learning and cloud deployment.
"""

role = "Software Engineer"
skills = "Python, AI, Cloud"
years = "5"

print("=== Sending request to AI model ===")
questions = generate_questions(sample_resume, role, skills, years)

# Debug output
print("\n=== Questions generated ===")
for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")

# Test cache behavior
print("\n=== Testing cache (should return instantly) ===")
questions_cached = generate_questions(sample_resume, role, skills, years)
for i, q in enumerate(questions_cached, 1):
    print(f"{i}. {q}")

print("\nAI test complete!")
