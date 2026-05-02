from sqlalchemy import select, func, or_, case, any_, cast
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.dialects.postgresql import ARRAY, TEXT
from infrastructure.postgres_db.orm_models import ChunkModel, DocumentModel
from core.logger import setup_logger
from core.schema import SearchResult, RetrievalFilter

logger = setup_logger(__name__)


class ChunkRepository:

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def search(
        self,
        query: str,
        document_ids: list[str] | None = None,
        top_k: int = 20
    ) -> list[SearchResult]:

        async with self._session_factory() as session:

            ts_query = func.to_tsquery("english", query)

            # 🔹 Rank (better version)
            rank = func.coalesce(
                func.ts_rank_cd(ChunkModel.tsv, ts_query), 0.0
            ).label("score")

            # 🔹 Base query
            stmt = select(
                ChunkModel.chunk_id,
                ChunkModel.raw_text.label("chunk"),
                rank
            ).where(
                ChunkModel.tsv.op("@@")(ts_query)
            )

            # 🔥 Apply document_id filter
            if document_ids:
                stmt = stmt.where(ChunkModel.document_id.in_(document_ids))

            # 🔹 Order + limit
            stmt = stmt.order_by(rank.desc()).limit(top_k)

            result = await session.execute(stmt)

            return [
                SearchResult(**row)
                for row in result.mappings()
            ]
            
    async def search_documents(self, filters: RetrievalFilter, top_k: int = 20):

        # --- safety: remove empty / bad terms ---
        terms = [t.strip() for t in filters.terms if t and t.strip()]
        if not terms:
            return []

        # --- patterns for ILIKE ---
        patterns = [f"%{t}%" for t in terms]

        async with self._session_factory() as session:
            ts_query_string = " | ".join(term.replace(" ", " & ") for term in terms)

            # --- safer full-text query ---
            ts_query_func = func.to_tsquery("english", ts_query_string)

            # --- ILIKE condition (ARRAY-based) ---
            ilike_condition = or_(*[
                ChunkModel.raw_text.ilike(p) for p in patterns
            ])

            # --- scoring boost for ILIKE ---
            ilike_score = case(
                (ilike_condition, 0.2),
                else_=0.0
            )

            # --- final rank ---
            rank = (
                func.ts_rank(ChunkModel.tsv, ts_query_func)
                + ilike_score
            )

            # --- main query ---
            query = (
                select(
                    DocumentModel.document_id,
                    DocumentModel.file_name,
                    func.max(rank).label("rank")
                )
                .join(ChunkModel)
                .where(
                    or_(
                        ChunkModel.tsv.op("@@")(ts_query_func),
                        ilike_condition
                    )
                )
                .group_by(
                    DocumentModel.document_id,
                    DocumentModel.file_name
                )
                .order_by(func.max(rank).desc())
                .limit(top_k)
            )

            result = await session.execute(query)

            return result.fetchall()
