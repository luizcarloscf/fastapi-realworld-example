from typing import Optional
from pydantic import BaseModel, EmailStr, SecretStr, ConfigDict


class UserModelView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    image: Optional[str]
    bio: Optional[str]
    hashed_password: str


class User(BaseModel):
    email: EmailStr
    username: str
    token: str
    bio: Optional[str] = None
    image: Optional[str] = None


class UserResponse(BaseModel):
    user: User


class NewUserRequest(BaseModel):
    email: EmailStr
    username: str
    password: SecretStr


class LoginUserRequest(BaseModel):
    email: EmailStr
    password: SecretStr


class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    bio: Optional[str] = None
    image: Optional[str] = None
