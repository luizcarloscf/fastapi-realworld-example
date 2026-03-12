from typing import Optional
from pydantic import BaseModel, EmailStr, SecretStr


class UserData(BaseModel):
    email: EmailStr
    username: str
    token: str
    bio: Optional[str] = None
    image: Optional[str] = None


class UserResponse(BaseModel):
    user: UserData


class UserRegistration(BaseModel):
    email: EmailStr
    username: str
    password: SecretStr


class UserRegistrationRequest(BaseModel):
    user: UserRegistration


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr


class UserLoginRequest(BaseModel):
    user: UserLogin


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    bio: Optional[str] = None
    image: Optional[str] = None


class UserUpdateRequest(BaseModel):
    user: UserUpdate
