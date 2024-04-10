from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from conduit.core.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    image = Column(String)
    bio = Column(String)
    hashed_password = Column(String)
