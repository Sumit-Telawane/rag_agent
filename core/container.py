"""
Dependency-injection container for the Storage Microservice (punq).

Singleton load order
--------------------
1. PostgreSQL  — AsyncSessionFactory registered as a singleton; engine pool
                 is created at module import of db_connection.
2. Milvus      — AsyncMilvusClient created inside the running event loop
                 (critical — see load_collection.py).
3. Repositories — receive their dependencies via constructor injection.
4. Orchestrator — receives both repositories via DI.

build_container() is async so it can await connect_milvus() safely within
the running uvicorn event loop.
"""

import punq
from sqlalchemy.ext.asyncio import async_sessionmaker

from infrastructure.postgres_db.db_connection import AsyncSessionFactory
from infrastructure.postgres_db.repositories.chunk_repository import ChunkRepository
from infrastructure.milvus_db.load_collection import connect_milvus
from infrastructure.milvus_db.repositories.vector_repository import VectorRepository
from core.services.retriver_agent import RetrievalService
from core.services.retriver_agent import StopWords, load_stopwords
from core.services.extractor_agent import ExtractorLLMService, ExtractorService
from core.logger import setup_logger

logger = setup_logger("container")


async def build_container() -> tuple[punq.Container, object]:
    """
    Build and return a fully-wired punq DI container and the Milvus client.

    Returns the Milvus client alongside the container so main.py can pass it
    to disconnect_milvus() on shutdown without reaching into module globals.

    Returns:
        (container, milvus_client)
    """
    container = punq.Container()

    container.register(
        StopWords,
        factory=load_stopwords,
        scope=punq.Scope.singleton,
    )

    # ---- PostgreSQL: register the session factory as a singleton ----
    container.register(
        async_sessionmaker,
        factory=lambda: AsyncSessionFactory,
        scope=punq.Scope.singleton,
    )

    # ---- Milvus: create AsyncMilvusClient inside the running event loop ----

    milvus_client = await connect_milvus()

    # ---- LLMS ----
    container.register(
        ExtractorLLMService,
        factory=lambda: ExtractorLLMService(),
        scope=punq.Scope.singleton,
    )

    # ---- Repositories ----
    doc_repo = ChunkRepository(
        session_factory=container.resolve(async_sessionmaker),
    )
    
    vec_repo = VectorRepository(client=milvus_client)

    container.register(
        ChunkRepository,
        factory=lambda: doc_repo,
        scope=punq.Scope.singleton,
    )

    container.register(
        VectorRepository,
        factory=lambda: vec_repo,
        scope=punq.Scope.singleton,
    )

    # ---- Services ----
    container.register(
        ExtractorService,
        factory=lambda: ExtractorService(
            llm_service=container.resolve(ExtractorLLMService),
            chunk_repository=container.resolve(ChunkRepository),
        ),
        scope=punq.Scope.singleton,
    )
    
    container.register(
        RetrievalService,
        factory=lambda: RetrievalService(
            chunk_repo=container.resolve(ChunkRepository),
            stopwords=container.resolve(StopWords),
        ),
        scope=punq.Scope.singleton,
    )

    # ---- Orchestrator ----

    return container, milvus_client