import asyncio
import json

from core.services.retriver_agent import RetrievalService
from infrastructure.postgres_db.db_connection import AsyncSessionFactory
from infrastructure.postgres_db.repositories.chunk_repository import ChunkRepository
from core.services.retriver_agent import load_stopwords
import os
from core.config import setting

os.environ["NLTK_DATA"] = setting.NLTK_DATA

async def main():
    session_factory = AsyncSessionFactory

    chunk_repo = ChunkRepository(session_factory)

    # 👇 explicitly load and inject
    stopwords = load_stopwords()
    service = RetrievalService(chunk_repo, stopwords)

    query = "Technical architecture overview of data engineering systems designed by Sumit Telawane"
    doc_ids = ["0a76ae37-344f-4e72-8205-a82160dd4cf7"]

    results = await service.execute(
        query=query,
        doc_ids=doc_ids,
        top_k=5
    )

    if results:
        data = json.dumps(
            [r.model_dump(mode="json") for r in results],
            indent=2
        )
        print(data)
        print(len(results))
    else:
        print("No results found")


if __name__ == "__main__":
    asyncio.run(main())