"""
Milvus repository — vector insert operations via AsyncMilvusClient.

AsyncMilvusClient (pymilvus >= 2.5.3) is natively async — no thread-pool
executor needed.
"""

from pymilvus import AsyncMilvusClient

from core.config import setting
from core.logger import setup_logger

logger = setup_logger("vector_repository")


class VectorRepository:
    """Handles all insert operations against the Milvus collection."""

    def __init__(self, client: AsyncMilvusClient) -> None:
        self._client = client