"""
Ingest route — POST /ingest


"""


from fastapi import APIRouter, HTTPException, Request, status

from core.logger import setup_logger
# from core.orchestrators.rag_agent_orchestrator import StorageOrchestrator


