from core.logger import setup_logger

logger = setup_logger(__name__)

from infrastructure.postgres_db.repositories.chunk_repository import ChunkRepository
import re

class StopWords(set):
    """Semantic type for DI clarity"""
    pass
def load_stopwords() -> StopWords:
    from nltk.corpus import stopwords
    return StopWords(stopwords.words("english"))

class RetrievalService:

    def __init__(self, chunk_repo: ChunkRepository, stopwords):
        self.chunk_repo = chunk_repo
        self.stopwords = stopwords

    def build_tsquery(self,query: str) -> str:
        # 1. lowercase
        query = query.lower()

        # 2. remove punctuation
        query = re.sub(r"[^\w\s]", " ", query)

        # 3. tokenize
        tokens = query.split()

        # 4. remove stopwords
        tokens = [t for t in tokens if t not in self.stopwords]

        # 5. deduplicate
        tokens = list(dict.fromkeys(tokens))

        # 6. build OR query
        return " | ".join(tokens)

    async def execute(
        self,
        query: str,
        doc_ids: list[str] | None = None,
        top_k: int = 10
    ):
        # 🔥 normalize query
        ts_query_str = self.build_tsquery(query)
        print(ts_query_str)


        if not ts_query_str:
            return None

        results = await self.chunk_repo.search(
            query=ts_query_str,
            document_ids=doc_ids,
            top_k=top_k
        )

        return results if results else None