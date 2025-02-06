from pydantic import BaseModel, Field

# Messaging


class UserCreate(BaseModel):
    username: str
    password: str


class ConversationCreate(BaseModel):
    title: str


# Tokens

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
