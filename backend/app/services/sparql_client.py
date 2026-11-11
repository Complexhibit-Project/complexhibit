from typing import Any, Dict, Optional

import httpx

from app.core.config import settings
from app.core.exceptions import SparqlQueryError


class SparqlClient:
    def __init__(
        self,
        endpoint_url: str = settings.VIRTUOSO_URL,
        default_graph: str = settings.DEFAULT_GRAPH_URL,
    ):
        self.endpoint_url = endpoint_url
        self.default_graph = default_graph
        # Timeout: 60s for reads (queries can be slow), 10s for connect
        self.timeout = httpx.Timeout(60.0, connect=10.0)

    async def query(self, query: str) -> Dict[str, Any]:
        """
        Execute a SPARQL SELECT query.
        """
        params = {"query": query, "format": "json", "default-graph-uri": self.default_graph}

        async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as client:
            try:
                response = await client.get(self.endpoint_url, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                raise SparqlQueryError(f"SPARQL query failed: {e.response.text}") from e
            except httpx.RequestError as e:
                raise SparqlQueryError(f"Connection error: {str(e)}") from e
            except Exception as e:
                raise SparqlQueryError(f"Unexpected error: {str(e)}") from e

    async def update(self, query: str) -> Dict[str, Any]:
        """
        Execute a SPARQL UPDATE query (INSERT/DELETE).
        """
        # Virtuoso often accepts updates via POST with the query in the body or as a parameter
        # Standard SPARQL Protocol uses 'update' parameter for POST
        data = {
            "query": query,  # Some endpoints use 'update', others 'query'. Virtuoso often supports 'query' for everything.
            # "default-graph-uri": self.default_graph # Updates might handle graphs differently (WITH clause)
        }

        # If default graph is needed for update, it might need to be in the query or params
        params = {}
        if self.default_graph:
            params["default-graph-uri"] = self.default_graph

        # Use /sparql-auth for updates to force authentication
        url = self.endpoint_url
        if url.endswith("/sparql"):
            url = url.replace("/sparql", "/sparql-auth")

        async with httpx.AsyncClient(timeout=self.timeout, trust_env=False) as client:
            try:
                # Using POST for updates with Digest Authentication
                auth = httpx.DigestAuth(settings.VIRTUOSO_USER, settings.VIRTUOSO_PASSWORD)
                response = await client.post(url, data=data, params=params, auth=auth)
                response.raise_for_status()
                # Updates might not return JSON, but we can try to parse it or return a success dict
                try:
                    return response.json()
                except:
                    return {"message": "Update successful", "response": response.text}
            except httpx.HTTPStatusError as e:
                raise SparqlQueryError(f"SPARQL update failed: {e.response.text}") from e
            except httpx.RequestError as e:
                raise SparqlQueryError(f"Connection error: {str(e)}") from e


sparql_client = SparqlClient()
