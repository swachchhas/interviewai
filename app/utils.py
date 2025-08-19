# app/utils.py
def allowed_file(filename: str, allowed: set) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed


def parse_skills(skills_raw: str):
    return [s.strip() for s in (skills_raw or "").split(",") if s.strip()]
