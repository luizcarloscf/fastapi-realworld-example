from typing import Optional
from typing_extensions import Annotated


from pydantic import BaseModel, EmailStr, Field, SecretStr, ConfigDict


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str


class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None


class User(BaseModel):
    email: EmailStr
    username: str
    token: str
    bio: Optional[str] = None
    image: Optional[str] = None


class NewUserRequest(BaseModel):
    email: EmailStr = Field(example="test@example.com")
    username: str
    password: SecretStr


class UserResponse(BaseModel):
    user: User


class LoginUserRequest(BaseModel):
    email: EmailStr = Field(example="test@example.com")
    password: SecretStr


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = Field(default=None, example="test@example.com")
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    bio: Optional[str] = None
    image: Optional[str] = None
