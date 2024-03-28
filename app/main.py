from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import SETTINGS
from app.core.database import Base, ENGINE
from app.api.routes import user

Base.metadata.create_all(bind=ENGINE)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=SETTINGS.ALLOWED_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user.router)
