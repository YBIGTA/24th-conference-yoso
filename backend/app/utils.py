import numpy as np
from sentence_transformers import SentenceTransformer

from app.models import Vector


model_name = "paraphrase-albert-small-v2"
model = SentenceTransformer(model_name)


def sanitize_text(text: str) -> str:
    """
    Sanitizes the input text by removing specific characters and 
    formatting it to lowercase.

    Args:
        text: The input text to be sanitized.

    Returns:
        A sanitized string where leading and trailing spaces, newline 
        characters, hyphens, and spaces are removed, and the text is 
        converted to lowercase.
    """
    return (
        text.strip()
        .replace('\n', '')
        .replace('-', '')
        .replace(' ', '')
        .lower()
    )


def create_embedding(
    domain: str,
    problem: str,
    solution: str,
) -> np.ndarray:
    """
    Creates an embedding by encoding and concatenating the given 
    domain, problem, and solution texts.

    Args:
        domain: The domain text to be included in the embedding.
        problem: The problem text to be included in the embedding.
        solution: The solution text to be included in the embedding.

    Returns:
        A numpy array representing the concatenated embeddings of the
        input texts.
    """
    sentences = [domain, problem, solution]
    
    return np.concatenate(model.encode(sentences))


def cosine_similarity(
    a: np.ndarray,
    b: np.ndarray
) -> float:
    """
    Computes the cosine similarity between two vectors.

    Args:
        a: The first vector.
        b: The second vector.

    Returns:
        A float representing the cosine similarity between the two
        input vectors. The value ranges from -1 to 1.
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def filter_by_similarity(
    src: np.ndarray,
    tgt_list: list[Vector],
    k: int
) -> list[dict]:
    """
    Filters and returns the top-k vectors from the target list based on 
    cosine similarity to the source vector.

    Args:
        src: The source vector to compare against.
        tgt_list: A list of `Vector` objects, each containing an id and 
            an embedding.
        k: The number of top similar vectors to return.

    Returns:
        A list of dictionaries containing the ids and similarity scores 
        of the top-k most similar vectors to the source vector.
    """
    scores = [{
        "id": vec.id,
        "score": cosine_similarity(src, vec.embedding)
    } for vec in tgt_list]

    scores.sort(reverse=True, key=lambda x: x["score"])

    return scores[:k]
