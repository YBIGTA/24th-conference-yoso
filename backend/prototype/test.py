import os
import numpy as np
import json
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer

# Environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
MONGODB_URI = os.getenv('MONGODB_URI')

NUM_QUERY_RESULTS = 20

# Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)
index_384 = pc.Index('384')
index_768 = pc.Index('768')

model_names = {
    'all-MiniLM-L6-v2': index_384,
    'multi-qa-MiniLM-L6-cos-v1': index_384,
    'paraphrase-albert-small-v2': index_768,
    'all-distilroberta-v1': index_768,
    'multi-qa-distilbert-cos-v1': index_768
}

models = [SentenceTransformer(name) for name in model_names]

lookup = {
    # 정양
    "4ec34634-304d-4315-91c6-4e3d5a7dcf2a": "MixFormer: Mixing Features across Windows and Dimensions",
    
    # 지민
    "b54ec221-30df-4069-9d0f-197dc97ada82": "A ConvNet for the 2020s",
    "d5c3b107-a247-4247-a522-9aff470360c1": "Attention Mechanisms in Computer Vision: A Survey",
    
    # 무현
    "8d26572a-7668-4cd2-b70a-52981c6b1383": "Masked Autoencoders Are Scalable Vision Learners",
    "95691b6c-b3d0-4f75-8214-e022df700195": "CYCLEMLP: A MLP-LIKE ARCHITECTURE FOR DENSE PREDICTION",

    # 세은
    "42d931df-28a7-47c6-ba66-1fc962769335": "CSWin Transformer: A General Vision Transformer Backbone with Cross-Shaped Windows ",
    "f0260487-2790-4b9b-8ab4-f67631d25683": "Glance-and-Gaze Vision Transformer",
    
    # 경윤
    "2b90c18f-bf38-4fa8-9d0c-22424b288d52": "SegFormer: Simple and Efficient Design for Semantic Segmentation with Transformers",
    "4ea3dbbe-ea8e-4bdd-bdd4-3134ba65092c": "MSG-Transformer: Exchanging Local Spatial Information by Manipulating Messenger Tokens",

    # 회수
    "35bdee85-bbf6-49cf-95d8-0ddc46bdc243": "Visformer: The Vision-friendly Transformer",
    "a70635d9-23ec-42cc-a1ee-f70e6c76ab46": "Co-Scale Conv-Attentional Image Transformers"
}


def concat_embedding(
    model: SentenceTransformer,
    domain: str, 
    problem: str, 
    solution: str
) -> np.ndarray:
    embeddings = model.encode([domain, problem, solution])
    return np.concatenate([emb for emb in embeddings]).tolist()


with open('dps-test.json', 'r') as file:
    dataset = json.load(file)

    results = [[] for _ in range(len(model_names))]

    for idx, data in enumerate(dataset):
        title = data['title']
        domain = data['domain']
        problem = data['problem']
        solution = data['solution']

        # Make embeddings
        embs = [concat_embedding(model, domain, problem, solution)
                for model in models]

        resps = []
        for model, emb in zip(model_names, embs):
            resps.append(model_names[model].query(
                namespace=model,
                vector=emb,
                top_k=NUM_QUERY_RESULTS
            )['matches'])

        for idx, resp in enumerate(resps):
            for i in range(NUM_QUERY_RESULTS):
                id = resp[i]['id']
                if id in lookup and lookup[id] == title:
                    results[idx].append({
                        "title": title,
                        "score": resp[i]["score"],
                        "rank": i
                    })

    stats = []
    for i, results in enumerate(results):
        avg = np.average([x['score'] for x in results])
        std = np.std([x['score'] for x in results])
        avg_rank = np.average([x['rank'] for x in results])

        stats.append({
            "model": list(model_names.keys())[i],
            "avg": avg,
            "std": std,
            "avg_rank": avg_rank
        })
    
    print(stats)
