from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils.text_cleaner import clean_question


def group_similar_questions(questions, threshold=0.45):
    if not questions:
        return []

    cleaned_questions = [clean_question(q) for q in questions]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(cleaned_questions)
    sim_matrix = cosine_similarity(tfidf_matrix)

    groups = []
    visited = set()

    for i in range(len(questions)):
        if i in visited:
            continue

        current_group = [questions[i]]
        visited.add(i)

        for j in range(i + 1, len(questions)):
            if j not in visited and sim_matrix[i][j] >= threshold:
                current_group.append(questions[j])
                visited.add(j)

        groups.append(current_group)

    return groups


def rank_predictions(groups):
    ranked = []

    for group in groups:
        representative = max(group, key=len)
        frequency_score = len(group)
        ranked.append((representative, frequency_score))

    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked