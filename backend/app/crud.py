from pymongo.collection import Collection
from sqlmodel import Session, select

from app.models import User, UserRegister, Paper
from app.core.security import get_password_hash, verify_password


def create_user(session: Session, user_data: UserRegister) -> User:
    user = User.model_validate(
        obj=user_data,
        update={"hashed_password": get_password_hash(user_data.password)}
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_user_by_email(session: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    user = session.exec(stmt).first()
    return user


def authenticate_user(
        session: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(session, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_paper_by_id(collection: Collection, paper_id: str) -> Paper | None:
    paper = collection.find_one({"_id": paper_id})
    return paper


def upsert_paper(collection: Collection, paper: Paper) -> Paper | None:
    paper_data = paper.model_dump()
    paper_data["_id"] = paper_data.pop("id")
    collection.update_one(
        filter={"_id": paper_data["_id"]},
        update={"$set": {
            k: paper_data[k] for k in paper_data if paper_data[k] is not None
        }},
        upsert=True
    )
    return None
