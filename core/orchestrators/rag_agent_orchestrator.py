"""
Storage Orchestrator — coordinates the full ingestion flow.

Flow
----
1. Build chunk rows (PG) + vector rows (Milvus) using shared deterministic UUIDs.
2. Write to PostgreSQL via DocumentRepository (owns its session lifecycle).
3. Write to Milvus after PG commits (Milvus has no rollback — write only on PG success).

Session management
------------------
The orchestrator has no knowledge of sessions or connections.
DocumentRepository handles the full PG transaction internally via the
injected AsyncSessionFactory.  The orchestrator simply calls the repo method
and awaits the result.
"""

import uuid

from core.logger import setup_logger

from core.utils.log_utils import log_error, log_info
from infrastructure.milvus_db.repositories.vector_repository import VectorRepository

logger = setup_logger("rag_orchestrator")


class RagOrchestrator:
    """
    Orchestrates document + chunk persistence across PostgreSQL and Milvus.

    Dependencies are injected via the DI container (punq).
    """

    def __init__(
        self,
        vector_repository: VectorRepository,
    ) -> None:
        self._vec_repo = vector_repository
