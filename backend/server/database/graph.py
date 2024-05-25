import os
from neo4j import Driver, Result, GraphDatabase
from pydantic import BaseModel, ValidationError

URI = os.getenv("NEO4J_URI")
AUTH = (os.getenv("NEO4J_AUTH_USER"), os.getenv("NEO4J_AUTH_PASSWORD"))


class Paper(BaseModel):
    paper_id: str
    title: str
    s_title: str = ""


def sanitize_title(
    title: str
) -> str:
    """Sanitize the title.

    Remove undesirable characters (e.g. '\n') and spaces, convert to lower case 
    to prevent duplicate nodes with same titles.
    
    Args:
        title: Input title string.

    Returns:
        A lowercased string with unwanted characters removed.
    """
    return (
        title
        .strip()
        .replace('\n', '')
        .replace('-', '')
        .replace(' ', '')
        .lower()
    )


def match_referenced_nodes(
    # driver: Driver,
    paper_id: str
) -> list[str]:
    """Fetches nodes that reference this node.

    Retrieves all nodes that reference(cite) this paper.

    Args:
        driver: Driver.
        paper_id: String ID value of target paper.

    Returns:
        A list of strings containing string ID values of nodes that reference
        this paper.
    """
    with GraphDatabase.driver(uri=URI, auth=AUTH) as driver:
        results, _, _ = driver.execute_query(
            "MATCH (p: Paper)-[:REFERENCES]->(q: Paper {paper_id: $paper_id}) "
            "WHERE p.paper_id IS NOT NULL "
            "RETURN p.paper_id",
            paper_id=paper_id
        )

    return [result["p.paper_id"] for result in results]


def match_referencing_nodes(
    # driver: Driver,
    paper_id: str
) -> list[str]:
    """Fetches nodes that this paper references.

    Retrieves all nodes that this paper references(cites).

    Args:
        driver: Driver.
        paper_id: String ID value of target paper.
    
    Returns:
        A list of strings containing string ID values of nodes that this paper
        references. Referenced papers that do not exist in NMJ DB, that is, ones 
        with no paper ID values, will be skipped.
    """
    with GraphDatabase.driver(uri=URI, auth=AUTH) as driver:
        results, _, _ = driver.execute_query(
            "MATCH (p: Paper {paper_id: $paper_id})-[:REFERENCES]->(q: Paper) "
            "WHERE q.paper_id IS NOT NULL "
            "RETURN q.paper_id",
            paper_id=paper_id
        )

    return [result["q.paper_id"] for result in results 
            if result["q.paper_id"] is not None]


def create_node(
    # driver: Driver, 
    id: str,
    title: str,
) -> str:
    """Creates a node.

    Creates a node for given paper. 

    Args:
        driver: Driver.
        id: String ID value.
        title: Title of the paper.

    Returns:
        String ID value of the node created.

    Raises:
        ValidationError: An error occured due to missing fields.
    """
    with GraphDatabase.driver(uri=URI, auth=AUTH) as driver:
        try:
            # Validate input
            paper = Paper(paper_id=id, title=title)
            paper.s_title = sanitize_title(paper.title)

            # Query
            result = driver.execute_query(
                "CREATE (p: Paper {paper_id: $paper_id, title: $title, s_title: $s_title})"
                "RETURN p.paper_id",
                parameters_=paper.model_dump(),
                result_transformer_=Result.single
            )

            return result['p.paper_id']
        except ValidationError as e:
            raise e


def create_relationship(
    # driver: Driver, 
    title: str, 
    ref_title: str
) -> tuple[str, str]:
    """Creates a reference relationship.

    Creates a reference relationship between nodes. If the node for referenced 
    paper does not exist, create one.
    
    Args:
        driver: Driver.
        title: Title of the referencing paper.
        ref_title: Title of the referenced paper.

    Returns:
        String ID values of referencing paper and referenced paper.
    """
    with GraphDatabase.driver(uri=URI, auth=AUTH) as driver:
        result = driver.execute_query(
            "MERGE (p: Paper {s_title: $s_title}) "
            "MERGE (q: Paper {s_title: $ref_s_title}) "
            "MERGE (p)-[:REFERENCES]->(q)"
            "RETURN p, q",
            s_title=sanitize_title(title),
            ref_s_title=sanitize_title(ref_title),
            result_transformer_=Result.single
        )

    return result['p']['s_title'], result['q']['s_title']

