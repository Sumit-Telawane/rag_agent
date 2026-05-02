"""
Pydantic schemas for the Storage Microservice.

"""

from typing import List, Optional
from pydantic import BaseModel, Field,field_validator
from uuid import UUID

class EmbedClientResponse(BaseModel):
    embeddings: List[List[float]]

class QueryDecomposition(BaseModel):
    steps: List[str] = Field(
        ..., 
        min_length=1, 
        max_length=5, 
        description="1 to 4 diverse search queries in proper format"
    )

class SearchResult(BaseModel):
    chunk_id:UUID
    chunk: str
    score: float

class RetrievalFilter(BaseModel):
    terms: List[str] = Field(default_factory=list)
