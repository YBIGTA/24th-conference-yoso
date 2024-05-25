import numpy as np
from pinecone import Pinecone, UpsertResponse
from sentence_transformers import SentenceTransformer
from server.core.config import settings

# Environment variables
PINECONE_API_KEY = settings.PINECONE_API_KEY
PINECONE_ENV = settings.PINECONE_ENV
PINECONE_INDEX = settings.PINECONE_INDEX

# Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)

model_name = "paraphrase-albert-small-v2"
model = SentenceTransformer(model_name)


def create_embedding(
    domain: str,
    problem: str,
    solution: str,
) -> np.ndarray:
    """Creates an embedding for given sentence."""
    sentences = [domain, problem, solution]
    
    return np.concatenate(model.encode(sentences))


def cosine_similarity(
    a: np.ndarray,
    b: np.ndarray
) -> float:
    """Calculates cosine similarity of two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def create_vector(
    id: str,
    domain: str,
    problem: str,
    solution: str,
) -> UpsertResponse:
    """Create and upsert vector into vector store."""
    vector = {
        "id": id,
        "values": create_embedding(domain, problem, solution),
    }

    return index.upsert(
        vectors=[vector],
        namespace=model_name
    )


def search_by_sentence(
    domain: str,
    problem: str,
    solution: str,
    k: int
) -> list[str]:
    """Fetches vectors similar to query sentence.
    
    Retrieves `k` most similar vectors from vector store. Embeddings for 
    domain, problem, solution are created and concatenated for constructing 
    query vector.

    Args:
        domain: Domain of the paper.
        problem: Problems of previous studies.
        solution: Solution suggested for solving the problem.
        k: Number of results to return.

    Returns:
        A list of string representing ID of returned vector.
    """
    vector = create_embedding(domain, problem, solution).tolist()
    
    res = index.query(
        namespace=model_name,
        vector=vector,
        top_k=k
    )

    return [vec["id"] for vec in res["matches"]]


def fetch_all_by_id(
    ids: list[str]
) -> list[dict]:
    """Fetches all vectors with given IDs.
    
    Args:
        ids: A list strings representing the ID of each vector.

    Returns:
        A list of dict, each containing ID and np.ndarray embedding values. For 
        example:

        [{
            'id': '2d55992d-2c6c-4d04-b52c-d90d75765ffe',
            'vector': array([ ... ])
        } ,{
            'id': '2eb6176a-ce47-48c9-af08-3c2aa742d6fa',
            'vector': array([ ... ])
        }]
    """
    results = index.fetch(ids=ids, namespace=model_name)["vectors"]
    
    return [{
        "id": results[id]["id"],
        "vector": np.asarray(results[id]["values"]),
    } for id in results]


def rank_by_similarity(
    src: np.ndarray,
    tgt: list[dict],
    k: int
) -> list[dict]:
    """Filters vector by similarity score.
    
    Args:
        src: A single source vector.
        tgt: A list of dict, each containing ID and embedding of the vector. For
          example:

          [{
            'id': '2d55992d-2c6c-4d04-b52c-d90d75765ffe',
            'vector': array([ ... ])
          } ,{
            'id': '2eb6176a-ce47-48c9-af08-3c2aa742d6fa',
            'vector': array([ ... ])
          }]

        k: Number of elements to return.

    Returns:
        A list of dict representing the ID and similarity scores of top K 
        vectors. For example:

        [{
            'id': '2d55992d-2c6c-4d04-b52c-d90d75765ffe',
            'score': 0.6173864743852904
        } ,{
            'id': '2eb6176a-ce47-48c9-af08-3c2aa742d6fa',
            'score': 0.6732818024842407
        }]
    """
    scores = [{
        "id": vec["id"],
        "score": cosine_similarity(src, vec["vector"])
    } for vec in tgt]

    scores.sort(reverse=True, key=lambda x: x["score"])

    return scores[:k]

