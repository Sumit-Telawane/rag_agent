import asyncio

from core.services.extractor_agent import (
    ExtractorService,
    ExtractorLLMService
)
from infrastructure.postgres_db.db_connection import AsyncSessionFactory
from infrastructure.postgres_db.repositories.chunk_repository import ChunkRepository


async def main():
    # --- DB setup ---
    session_factory = AsyncSessionFactory
    chunk_repo = ChunkRepository(session_factory)

    # --- LLM service ---
    llm_service = ExtractorLLMService()

    # --- Main service ---
    service = ExtractorService(
        llm_service=llm_service,
        chunk_repository=chunk_repo
    )

    # --- Test query ---
    query = "Technical architecture overview of data engineering systems designed by Sumit Telawane"

    results = await service.execute(query)

    print("\n🔍 Query:", query)
    print("\n📄 Results:")
    
    for r in results:
        print({
            "document_id": str(r.document_id),
            "file_name": r.file_name,
            "rank": float(r.rank) if r.rank else None
        })


if __name__ == "__main__":
    asyncio.run(main())