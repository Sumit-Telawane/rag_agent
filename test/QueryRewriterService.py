import asyncio

from core.services.query_rewriter_agent import (
    QueryRewriterLLMService,
    QueryRewriterService
)


async def main():
    # initialize services
    llm_service = QueryRewriterLLMService()
    service = QueryRewriterService(llm_service)

    # test query
    query = "what was the role of sumit telawane as data engineer"

    result = await service.execute(query)

    print("Original Query:")
    print(query)

    print("\nRewritten Query:")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())