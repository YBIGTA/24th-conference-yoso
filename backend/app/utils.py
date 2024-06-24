import boto3
import numpy as np
import urllib
from fastapi import UploadFile
from sentence_transformers import SentenceTransformer

from app.core.config import settings
from app.models import Vector


model_name = "paraphrase-albert-small-v2"
model = SentenceTransformer(model_name)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
)


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


def create_embedding(domain: str, problem: str, solution: str) -> np.ndarray:
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


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
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
        src: np.ndarray, tgt_list: list[Vector], k: int) -> list[dict]:
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


def upload_file_to_s3(file: UploadFile, dir: str) -> str | None:
    """
    Uploads a file to an S3 bucket.

    Args:
        file: The file to be uploaded.
        dir: The directory in the S3 bucket where the file will be 
            uploaded.

    Returns:
        The URL of the uploaded file if the upload is successful, 
        otherwise None.
    """
    if not file:
        return None
    try:
        s3_client.upload_fileobj(
            Fileobj=file.file,
            Bucket=settings.S3_BUCKET_NAME,
            Key=f"{dir}/{file.filename}"
        )
    except:
        return None
    url = f"https://s3-ap-northeast-2.amazonaws.com/{settings.S3_BUCKET_NAME}/{urllib.parse.quote(f"{dir}/{file.filename}", safe="~()*!.'")}"
    return url
