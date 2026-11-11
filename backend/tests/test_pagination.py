import asyncio
import unittest
import sys
import os
sys.path.append(os.getcwd())

from unittest.mock import AsyncMock, MagicMock
from app.utils.cursor import encode_cursor, decode_cursor
from app.routers.institutions import all_instituciones
from app.services.sparql_client import SparqlClient

class TestPagination(unittest.TestCase):
    def test_cursor_encoding(self):
        cursor = encode_cursor("Test Label", "http://test.uri")
        decoded = decode_cursor(cursor)
        self.assertEqual(decoded, ("Test Label", "http://test.uri"))

    def test_pagination_flow(self):
        asyncio.run(self._async_test_pagination_flow())

    async def _async_test_pagination_flow(self):
        # Mock SPARQL client
        mock_client = AsyncMock(spec=SparqlClient)
        
        # Simulate response for page 1 (returns 11 items for page_size=10)
        # The router expects a list of dicts from parse_sparql_response, 
        # but here we are mocking the client.query response which is then parsed.
        # However, the router calls parse_sparql_response(response).
        # We need to mock what client.query returns such that parse_sparql_response works, 
        # OR we can mock parse_sparql_response too.
        # But wait, the router code imports parse_sparql_response.
        # Let's just mock the client.query return value to match what rdflib returns?
        # Or easier: since we are testing the router logic *after* the query, 
        # let's assume client.query returns something that parse_sparql_response handles.
        # Actually, let's just mock the whole flow by mocking client.query to return a structure
        # that parse_sparql_response turns into a list.
        
        # BUT, since we can't easily import parse_sparql_response to see what it expects without reading code,
        # let's try to mock the *result* of parse_sparql_response if we could patch it.
        # Since we can't patch easily without unittest.mock.patch, let's try that.
        
        with unittest.mock.patch('app.routers.institutions.parse_sparql_response') as mock_parse:
            # Setup mock return value for parse_sparql_response
            # Return 11 items
            mock_parse.return_value = [
                {"label": f"Inst {i}", "uri": f"http://ex/{i}"} 
                for i in range(11)
            ]
            
            # Call endpoint
            response = await all_instituciones(cursor=None, page_size=10, client=mock_client)
            # response is ORJSONResponse
            import json
            body = json.loads(response.body)
            
            self.assertIn("next_cursor", body)
            self.assertIsNotNone(body["next_cursor"])
            self.assertEqual(len(body["data"]), 10) # Should be trimmed to 10
            
            # Verify query was called with correct LIMIT 11
            call_args = mock_client.query.call_args[0][0]
            self.assertIn("LIMIT 11", call_args)
            self.assertNotIn("OFFSET", call_args)

if __name__ == "__main__":
    unittest.main()
