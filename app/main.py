from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token, get_password_hash, UserDependency
from database import create_record, get_session, SessionDependency, is_user
from validation import ConversationCreate, Token, UserCreate
from models import Message, User, Conversation
from config import config
from fastapi.middleware.cors import CORSMiddleware

from llm.model import Model
from llm.chroma import ChromaDBManager

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


# Initialize Model
chroma_db = ChromaDBManager(db_path=config.CHROMA_DB_PATH)
model = Model(chroma=chroma_db)


@app.post("/create-user", status_code=status.HTTP_201_CREATED)
async def user(user: UserCreate, db: SessionDependency):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)

    if is_user(user.username, db):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    create_record(db_user, db)

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
async def create_conversation(conversation: ConversationCreate, user: UserDependency, db: SessionDependency):
    db_conversation = Conversation(
        title=conversation.title,
        user_id=user.id
    )
    create_record(db_conversation, db)
    return {"title": "conversation.title"}


@app.get("/conversations")
async def fetch_conversations(user: UserDependency, db: SessionDependency):
    result = db.query(Conversation.name).filter(
        Conversation.user_id == user.id).all()
    return [{"title": res.title} for res in result]


async def get_messages(title: str, user_id, db: SessionDependency):
    conversation = db.query(Conversation).filter(
        (Conversation.user_id == user_id) &
        (Conversation.title == title)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation does not exist")

    messages = db.query(Message)


@app.post("/message", status_code=status.HTTP_201_CREATED)
async def message(title: str, message_text: str, user: UserDependency, db: SessionDependency):
    # Retrieve Conversation to get Conversation_id
    conversation = db.query(Conversation).filter(
        (Conversation.user_id == user.id) &
        (Conversation.title == title)
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Conversation does not exist")

    # Fetch conversation history
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).all()

    history = history = "\n".join(
        f"{'User' if i % 2 == 0 else 'LLM'}: {message.message_text}"
        for i, message in enumerate(messages)
    )

    # Get LLM response
    llm_response = model.query(query=message_text, history=history)

    # Save user's message
    user_message = Message(
        conversation_id=conversation.id,
        message_text=message_text,
        sent_at=datetime.utcnow()  # Add timestamp for user's message
    )
    create_record(user_message, db)

    # Save LLM's response
    llm_message = Message(
        conversation_id=conversation.id,
        message_text=llm_response,
        sent_at=datetime.utcnow()  # Add timestamp for LLM's response
    )
    create_record(llm_message, db)

    return {"response": llm_response}
