import httpx
from core.schema import EmbedClientResponse


class EmbeddingClient:
    """
    HTTP client for embedding service.

    Expects:
        POST /embed/query
        {
            "queries": [str, str, ...]
        }

    Returns:
        {
            "embeddings": [[float, ...], ...]
        }
    """

    def __init__(self, base_url: str, timeout: float = 600.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=timeout,
        )

    def create_embeddings(self, texts: list[str]) -> list[EmbedClientResponse]:
        response = self._client.post(
            "/embed/query",
            json={"queries": texts},
        )
        response.raise_for_status()

        payload = response.json()

        return EmbedClientResponse(**payload)

    def close(self) -> None:
        self._client.close()