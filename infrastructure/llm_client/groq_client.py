import asyncio
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

query_llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_retries=2,
    reasoning_format='hidden'
)

retriver_llm = ChatGroq(
    model="qwen/qwen3-32b",
    temperature=0,
    max_retries=2,
)



# from core.utils.helper import load_prompt
# system_prompt = load_prompt(
#     r"D:\dev\rag\rag_agents\prompts\query_decomposition_prompt.txt"
# )

# user_query = "How does Docling compare with other document processing tools in accuracy speed and structured output quality"

# from langchain_core.messages import SystemMessage, HumanMessage
# from core.schema import QueryDecomposition
# messages = [
#     SystemMessage(content=system_prompt),
#     HumanMessage(content=user_query)
# ]

# structured_llm = query_llm.with_structured_output(QueryDecomposition)

# async def main():
#     response = await structured_llm.ainvoke(messages)
#     print(response.steps)

# if __name__ == "__main__":
#     asyncio.run(main())