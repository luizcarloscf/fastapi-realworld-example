from typing import Optional

from pydantic import BaseModel


class ProfileData(BaseModel):
    username: str
    bio: Optional[str]
    image: Optional[str]
    following: Optional[bool] = None


class ProfileResponse(BaseModel):
    profile: ProfileData
