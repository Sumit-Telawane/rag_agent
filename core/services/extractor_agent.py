from core.logger import setup_logger

logger = setup_logger(__name__)

from langchain_core.messages import SystemMessage, HumanMessage
from core.schema import RetrievalFilter
from infrastructure.llm_client.groq_client import retriver_llm
from infrastructure.postgres_db.repositories.chunk_repository import ChunkRepository
from core.utils.helper import load_prompt
from core.config import setting


class ExtractorLLMService:

    def __init__(self):
        self.prompt = load_prompt(setting.EXTRACTOR_PROMPT)

        self.structured_llm = retriver_llm.with_structured_output(
            RetrievalFilter,
            method="json_mode"
        )

    async def generate(self, query: str) -> RetrievalFilter:
        messages = [
            SystemMessage(content=self.prompt),
            HumanMessage(content=query)
        ]

        response = await self.structured_llm.ainvoke(messages)

        # fallback
        if not response.terms:
            response.terms = [query.lower()]

        return response
    
class ExtractorService:

    def __init__(
        self,
        llm_service: ExtractorLLMService,
        chunk_repository: ChunkRepository
    ):
        self.llm_service = llm_service
        self.chunk_repository = chunk_repository

    async def execute(self, query: str):
        filters: RetrievalFilter = await self.llm_service.generate(query)
        print(filters)

        filters = self._normalize(filters)

        results = await self.chunk_repository.search_documents(
            filters=filters
        )

        return results

    def _normalize(self, filters: RetrievalFilter) -> RetrievalFilter:
        def clean(text: str) -> str:
            return text.lower().replace("\n", " ").strip()

        return RetrievalFilter(
            terms=[
                clean(t) for t in filters.terms
                if t and t.strip()
            ]
        )