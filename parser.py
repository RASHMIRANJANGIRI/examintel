import re
from utils.text_cleaner import normalize_text

TRIGGER_WORDS = [
    "define", "explain", "describe", "discuss", "what is",
    "write short note", "differentiate", "compare", "derive",
    "state", "mention", "list", "justify", "elaborate",
    "comment on", "why", "how", "write"
]

def split_into_questions(text):
    text = normalize_text(text)
    lines = text.split("\n")

    questions = []
    buffer = ""

    for line in lines:
        line = line.strip()

        if len(line) < 5:
            continue

        if re.match(r"^(\d+[\).]|q[\.\-\s]?\d+|question\s*\d+)", line, re.IGNORECASE):
            if buffer:
                questions.append(buffer.strip())
            buffer = line
        else:
            if buffer:
                buffer += " " + line
            elif any(word in line.lower() for word in TRIGGER_WORDS):
                buffer = line

        if buffer and line.endswith("?"):
            questions.append(buffer.strip())
            buffer = ""

    if buffer:
        questions.append(buffer.strip())

    final_questions = []
    for q in questions:
        q = re.sub(r"\s+", " ", q).strip()
        if len(q) > 12:
            final_questions.append(q)

    return final_questions

def detect_marks(question):
    match = re.search(r"(\d+)\s*marks?", question, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None