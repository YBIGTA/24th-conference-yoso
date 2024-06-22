import numpy as np
from neo4j import Driver, Result
from pinecone import Index, UpsertResponse
from pymongo.collection import Collection
from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    User, 
    UserRegister, 
    Paper, 
    PaperQuery, 
    GraphNodeBase, 
    GraphNode
)
from app.utils import sanitize_text, create_embedding, model_name


def create_user(session: Session, user_data: UserRegister) -> User:
    user = User.model_validate(
        obj=user_data,
        update={"hashed_password": get_password_hash(user_data.password)}
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_username(session: Session, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    user = session.exec(stmt).first()
    return user


def authenticate_user(
        session: Session, username: str, password: str) -> User | None:
    user = get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_paper_by_id(collection: Collection, paper_id: str) -> Paper | None:
    paper = collection.find_one({"_id": paper_id})
    return paper


def upsert_paper(collection: Collection, paper: Paper) -> str:
    paper_data = paper.model_dump()
    paper_data["_id"] = paper_data.pop("id")
    result = collection.update_one(
        filter={"_id": paper_data["_id"]},
        update={"$set": {
            k: paper_data[k] for k in paper_data if paper_data[k] is not None
        }},
        upsert=True
    )
    return result.upserted_id


def create_graph_node(driver: Driver, node_data: GraphNodeBase) -> str:
    node = GraphNode(
        paper_id=node_data.paper_id,
        title=node_data.title,
        s_title=sanitize_text(node_data.title)
    )
    result = driver.execute_query(
        "MERGE (p: Paper {s_title: $s_title}) "
        "SET p.paper_id = $paper_id "
        "SET p.title = $title "
        "RETURN p.paper_id",
        parameters_=node.model_dump(),
        result_transformer_=Result.single
    )
    return result["p.paper_id"]


def create_graph_relationship(driver: Driver, title: str, ref_title: str):
    result = driver.execute_query(
        "MERGE (p: Paper {s_title: $s_title}) "
        "MERGE (q: Paper {s_title: $ref_s_title}) "
        "MERGE (p)-[:REFERENCES]->(q)"
        "RETURN p, q",
        s_title=sanitize_text(title),
        ref_s_title=sanitize_text(ref_title),
        result_transformer_=Result.single
    )
    return result['p']['s_title'], result['q']['s_title']


def get_citation_nodes(driver: Driver, paper_id: str) -> list[str]:
    results, _, _ = driver.execute_query(
        "MATCH (p: Paper)-[:REFERENCES]->(q: Paper {paper_id: $paper_id}) "
        "WHERE p.paper_id IS NOT NULL "
        "RETURN p.paper_id",
        paper_id=paper_id
    )
    return [result["p.paper_id"] for result in results]


def get_reference_nodes(driver: Driver, paper_id: str) -> list[str]:
    results, _, _ = driver.execute_query(
        "MATCH (p: Paper {paper_id: $paper_id})-[:REFERENCES]->(q: Paper) "
        "WHERE q.paper_id IS NOT NULL "
        "RETURN q.paper_id",
        paper_id=paper_id
    )
    return [result["q.paper_id"] for result in results 
            if result["q.paper_id"] is not None]


def create_vector(index: Index, id: str, text: PaperQuery) -> UpsertResponse:
    """Create and upsert vector into vector store."""
    vector = {
        "id": id,
        "values": create_embedding(text.domain, text.problem, text.solution),
    }
    return index.upsert(vectors=[vector], namespace=model_name)


def get_vector_ids_by_sentence(
        index: Index, text: PaperQuery, k: int) -> list[str]:
    vector = create_embedding(text.domain, text.problem, text.solution).tolist()
    res = index.query(
        namespace=model_name,
        vector=vector,
        top_k=k
    )
    return [vec["id"] for vec in res["matches"]]


def get_vectors_by_ids(index: Index, ids: list[str]) -> list[dict]:
    results = index.fetch(ids=ids, namespace=model_name)["vectors"]
    return [{
        "id": results[id]["id"],
        "vector": np.asarray(results[id]["values"]),
    } for id in results]

