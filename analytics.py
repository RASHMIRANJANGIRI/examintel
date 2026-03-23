import pandas as pd
from collections import Counter
from utils.text_cleaner import clean_question

STOPWORDS = {
    "the", "is", "a", "an", "of", "to", "and", "in", "for", "on",
    "with", "by", "what", "how", "why", "define", "explain",
    "describe", "discuss", "write", "state", "derive", "compare",
    "differentiate", "short", "note"
}

def extract_keywords(questions, top_n=20):
    all_words = []
    for q in questions:
        cleaned = clean_question(q)
        words = cleaned.split()
        all_words.extend([w for w in words if w not in STOPWORDS and len(w) > 2])

    if not all_words:
        return pd.Series(dtype=int)

    return pd.Series(Counter(all_words)).sort_values(ascending=False).head(top_n)

def infer_topic(question, keyword_series):
    q = clean_question(question)
    for word in keyword_series.index:
        if word in q:
            return word
    return "general"