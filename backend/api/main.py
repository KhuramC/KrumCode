import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag.query import initialize_query_engine
from utils.config_loader import get_config

from . import rest

logger = logging.getLogger("api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()

    app.state.query_engine = initialize_query_engine(config)
    logger.info("RAG query engine initialized.")
    yield
    logger.info("Shutting down.")


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rest.router)
