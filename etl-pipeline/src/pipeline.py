"""
ETL Pipeline Orchestrator

Main entry point for the OntoExhibit data transformation pipeline.
Orchestrates the download, normalization, and transformation of data
from pathwise.db to RDF triples for Virtuoso.
"""
import os
import sys
import time
import requests

# Add src directory to path for imports
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PIPELINE_ROOT = os.path.dirname(SRC_DIR)
sys.path.insert(0, SRC_DIR)
sys.path.insert(0, PIPELINE_ROOT)


# Configuration
DATABASE_URL = 'https://microsites.iarthislab.eu/assets/static/pathwise.db'
DATABASE_FILE = 'pathwise.db'
OUTPUT_DIR = os.path.join(PIPELINE_ROOT, 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'result.nt')


def print_separator(message: str):
    """Print a formatted separator with message."""
    print('------------------------------------------------------')
    print(message)
    print('------------------------------------------------------\n')


def download_updated_database():
    """Download the latest version of pathwise.db."""
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f'The file {DATABASE_FILE} has been deleted successfully\n')
    else:
        print(f'The file {DATABASE_FILE} does not exist!\n')
    
    try:
        print(f'Downloading from {DATABASE_URL}...')
        r = requests.get(DATABASE_URL, allow_redirects=True)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Error downloading database: {e}")
    
    try:
        with open(DATABASE_FILE, 'wb') as f:
            f.write(r.content)
        print(f'Downloaded {len(r.content)} bytes\n')
    except IOError as e:
        raise SystemExit(f"Error writing database file: {e}")


def run_normalize_db():
    """Run database normalization scripts."""
    from normalization import normalize_db  # noqa: F401
    print('normalize_db.py completed\n')


def run_normalize_places():
    """Run place normalization scripts."""
    from normalization import normalize_places  # noqa: F401
    print('normalize_places.py completed\n')


def run_transform_data():
    """Run the RDF transformation."""
    from transformation import transform_data  # noqa: F401
    print('transform_data.py completed\n')


def move_output_to_backend():
    """Copy result.nt to the backend directory."""
    import shutil
    
    backend_dir = os.path.join(os.path.dirname(PIPELINE_ROOT), 'backend')
    backend_result = os.path.join(backend_dir, 'result.nt')
    
    if os.path.exists('result.nt'):
        # Ensure output directory exists
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
        # Copy to output directory
        shutil.copy('result.nt', OUTPUT_FILE)
        print(f'Copied result.nt to {OUTPUT_FILE}')
        
        # Copy to backend if it exists
        if os.path.exists(backend_dir):
            shutil.copy('result.nt', backend_result)
            print(f'Copied result.nt to {backend_result}')
    else:
        print('Warning: result.nt was not generated')


def main():
    """Run the complete ETL pipeline."""
    start_time = time.time()
    
    print_separator('Step 1/4: Downloading updated database...')
    download_updated_database()
    
    print_separator('Step 2/4: Running normalize_db.py...')
    run_normalize_db()
    
    print_separator('Step 3/4: Running normalize_places.py...')
    run_normalize_places()
    
    print_separator('Step 4/4: Running transform_data.py...')
    run_transform_data()
    
    print_separator('Moving output to backend...')
    move_output_to_backend()
    
    elapsed = time.time() - start_time
    print(f'\n{"="*54}')
    print(f'Pipeline completed in {elapsed:.2f} seconds')
    print(f'{"="*54}\n')


if __name__ == '__main__':
    main()
