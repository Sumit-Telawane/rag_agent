from langchain_core.messages import SystemMessage, HumanMessage
from core.schema import QueryDecomposition
from core.utils.helper import load_prompt
from infrastructure.llm_client.groq_client import query_llm
from core.config import setting

class QueryRewriterLLMService:
    def __init__(self):
        self.prompt = load_prompt(setting.QUERY_REWRITER_PROMPT)

        self.structured_llm = query_llm.with_structured_output(
            QueryDecomposition,
            method="json_mode"
        )

    async def generate(self, query: str) -> QueryDecomposition:
        messages = [
            SystemMessage(content=self.prompt),
            HumanMessage(content=query)
        ]

        response = await self.structured_llm.ainvoke(messages)

        return response

class QueryRewriterService:

    def __init__(self, llm_service: QueryRewriterLLMService):
        self.llm_service = llm_service

    async def execute(self, query: str) -> str:
        result = await self.llm_service.generate(query)

        return result.steps[0] if result.steps else query