from typing import Optional
from pydantic import BaseModel, EmailStr, SecretStr, Field, field_validator


class UserData(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=6, max_length=30)
    token: str
    bio: Optional[str] = None
    image: Optional[str] = None


class UserResponse(BaseModel):
    user: UserData


class UserRegistration(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=6, max_length=30)
    password: SecretStr = Field(..., min_length=6, max_length=30)


class UserRegistrationRequest(BaseModel):
    user: UserRegistration


class UserLogin(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=6, max_length=30)


class UserLoginRequest(BaseModel):
    user: UserLogin


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=6, max_length=30)
    password: Optional[SecretStr] = Field(None, min_length=6, max_length=30)
    bio: Optional[str] = None
    image: Optional[str] = None

    @field_validator("username", "email", "password", mode="before")
    @classmethod
    def check_not_none_if_set(cls, v):
        if v is None:
            raise ValueError(f"Field cannot be set to null")
        return v

    @field_validator("bio", "image", mode="before")
    @classmethod
    def normalize_to_none(cls, v):
        if isinstance(v, str) and len(v.strip()) == 0:
            return None
        return v


class UserUpdateRequest(BaseModel):
    user: UserUpdate
