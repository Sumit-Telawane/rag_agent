from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.postgres_db.orm_models import DocumentModel


class DocumentRepository:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def get_document_id_by_name(self, document_name: str) -> str | None:

        async with self._session_factory() as session:

            stmt = select(DocumentModel.document_id).where(
                func.lower(DocumentModel.file_name).like(f"%{document_name.lower()}%")
            )

            result = await session.execute(stmt)
            row = result.first()

            return str(row.document_id) if row else None