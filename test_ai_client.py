# test_ai_client.py
from app.ai_client import generate_questions

resume_text = """
John Doe
Software Engineer with experience in Python, Flask, and data analysis.
Worked on projects involving REST APIs, web scraping, and database optimization.
"""

role = "Backend Developer"
skills = "Python, Flask, SQL"
years = "3"

questions = generate_questions(resume_text, role, skills, years)

print("Generated Questions:")
for i, q in enumerate(questions, 1):
    print(f"{i}. {q}")
