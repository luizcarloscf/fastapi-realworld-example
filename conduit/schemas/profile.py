from typing import Optional

from pydantic import BaseModel


class ProfileData(BaseModel):
    username: str
    bio: Optional[str]
    image: Optional[str]
    following: bool = False


class ProfileResponse(BaseModel):
    profile: ProfileData
