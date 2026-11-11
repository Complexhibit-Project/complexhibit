"""
Virtuoso Data Loader

Loads RDF N-Triples data into Virtuoso triplestore using SPARQL UPDATE.
Configured for the docker-compose Virtuoso instance.
"""
import os
import requests
from typing import Optional


# Configuration from environment or defaults matching docker-compose.yml
VIRTUOSO_URL = os.getenv('VIRTUOSO_URL', 'http://localhost:8890/sparql')
VIRTUOSO_GRAPH_URI = os.getenv('VIRTUOSO_GRAPH_URI', 'http://localhost:8890/DAV/home/dba/rdf_sink')
VIRTUOSO_USER = os.getenv('VIRTUOSO_USER', 'dba')
VIRTUOSO_PASSWORD = os.getenv('VIRTUOSO_DBA_PASSWORD', 'dba')


def clear_graph(graph_uri: str = VIRTUOSO_GRAPH_URI) -> bool:
    """
    Clear all triples from a named graph.
    
    Args:
        graph_uri: The URI of the graph to clear
        
    Returns:
        True if successful, False otherwise
    """
    query = f"CLEAR GRAPH <{graph_uri}>"
    
    try:
        response = requests.post(
            VIRTUOSO_URL,
            data={'query': query},
            auth=(VIRTUOSO_USER, VIRTUOSO_PASSWORD),
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        print(f"Cleared graph: {graph_uri}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error clearing graph: {e}")
        return False


def load_ntriples_file(file_path: str, graph_uri: str = VIRTUOSO_GRAPH_URI, 
                       batch_size: int = 1000) -> tuple[int, int]:
    """
    Load N-Triples file into Virtuoso in batches.
    
    Args:
        file_path: Path to the .nt file
        graph_uri: Target graph URI
        batch_size: Number of triples per INSERT batch
        
    Returns:
        Tuple of (successful_triples, failed_triples)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    successful = 0
    failed = 0
    batch = []
    
    print(f"Loading {file_path} into graph {graph_uri}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            batch.append(line)
            
            if len(batch) >= batch_size:
                success = _insert_batch(batch, graph_uri)
                if success:
                    successful += len(batch)
                else:
                    failed += len(batch)
                batch = []
                
                if line_num % 10000 == 0:
                    print(f"  Processed {line_num} lines...")
    
    # Insert remaining triples
    if batch:
        success = _insert_batch(batch, graph_uri)
        if success:
            successful += len(batch)
        else:
            failed += len(batch)
    
    print(f"Loaded {successful} triples, {failed} failed")
    return successful, failed


def _insert_batch(triples: list[str], graph_uri: str) -> bool:
    """Insert a batch of triples into Virtuoso."""
    triples_str = '\n'.join(triples)
    query = f"INSERT DATA {{ GRAPH <{graph_uri}> {{ {triples_str} }} }}"
    
    try:
        response = requests.post(
            VIRTUOSO_URL,
            data={'query': query},
            auth=(VIRTUOSO_USER, VIRTUOSO_PASSWORD),
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=60
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error inserting batch: {e}")
        return False


def count_triples(graph_uri: str = VIRTUOSO_GRAPH_URI) -> Optional[int]:
    """
    Count the number of triples in a graph.
    
    Returns:
        Number of triples or None if error
    """
    query = f"SELECT (COUNT(*) as ?count) WHERE {{ GRAPH <{graph_uri}> {{ ?s ?p ?o }} }}"
    
    try:
        response = requests.get(
            VIRTUOSO_URL,
            params={'query': query, 'format': 'json'},
            auth=(VIRTUOSO_USER, VIRTUOSO_PASSWORD),
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        count = int(data['results']['bindings'][0]['count']['value'])
        return count
    except Exception as e:
        print(f"Error counting triples: {e}")
        return None


def reload_data(file_path: str, graph_uri: str = VIRTUOSO_GRAPH_URI) -> bool:
    """
    Clear graph and reload data from file.
    
    This is the main function for refreshing the triplestore
    after running the ETL pipeline.
    
    Args:
        file_path: Path to result.nt
        graph_uri: Target graph URI
        
    Returns:
        True if successful
    """
    print("=" * 50)
    print("Reloading data into Virtuoso")
    print("=" * 50)
    
    # Clear existing data
    if not clear_graph(graph_uri):
        print("Warning: Could not clear graph, proceeding anyway...")
    
    # Load new data
    try:
        successful, failed = load_ntriples_file(file_path, graph_uri)
        
        # Verify
        count = count_triples(graph_uri)
        if count is not None:
            print(f"Graph now contains {count} triples")
        
        return failed == 0
    except Exception as e:
        print(f"Error reloading data: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # Default to output directory
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            'output', 'result.nt'
        )
    
    reload_data(file_path)
