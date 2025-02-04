from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token, get_password_hash, UserDependency
from database import create_user, get_session, SessionDependency, is_user
from validation import Token, UserCreate
from models import User, Conversation
from config import config
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # Allow cookies or authentication headers if needed
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.post("/create-user", status_code=status.HTTP_201_CREATED)
async def user(user: UserCreate, db: SessionDependency):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)

    if is_user(user.username, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    create_user(db_user, db)

    # Create access token
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/refresh-token")
async def refresh_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDependency
) -> Token:
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.post("/create-conversation", status_code=status.HTTP_201_CREATED)
async def create_conversation(user: UserDependency, db: SessionDependency):
    conversation = Conversation(title = "")


@app.get("/conversations")
async def fetch_conversation(user: UserDependency, db: SessionDependency):
    result = db.query(Conversation.name).filter(
        Conversation.user_id == user.id).all()
    return [res.name for res in result]


# @app.post("/conversations/", status_code=status.HTTP_201_CREATED)
# def create_conversation(conversation: ConversationCreate, user: UserDependency):
#     db_conversation = Conversation(**conversation.dict())
#     db.add(db_conversation)
#     db.commit()
#     db.refresh(db_conversation)
#     return db_conversation
