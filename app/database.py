from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, User
from typing import Annotated
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from config import config

# Create engine
engine = create_engine(config.DATABASE_URL, connect_args={
                       "check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


SessionDependency = Annotated[Session, Depends(get_session)]

# Methods


def get_user(username: str, db: Session):
    user = db.query(User).where(User.username == username).first()
    return user


def is_user(username: str, db: Session):
    return get_user(username, db) is not None


def create_user(user: User, db: Session):
    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError as e:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise
