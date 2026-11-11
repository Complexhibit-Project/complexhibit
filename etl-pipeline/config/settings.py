"""
ETL Pipeline Configuration Settings

Centralized configuration for the OntoExhibit ETL pipeline.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Ontology Configuration
URI_ONTOLOGIA = os.getenv('URI_ONTOLOGIA', 'https://w3id.org/OntoExhibit#')

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', 'pathwise.db')
DATABASE_DOWNLOAD_URL = 'https://microsites.iarthislab.eu/assets/static/pathwise.db'

# Stardog Configuration (legacy)
DATABASE_STARDOG = os.getenv('DATABASE_STARDOG')
ENDPOINT_STARDOG = os.getenv('ENDPOINT_STARDOG')
USERNAME_STARDOG = os.getenv('USERNAME_STARDOG')
PASSWORD_STARDOG = os.getenv('PASSWORD_STARDOG')

# Virtuoso Configuration
VIRTUOSO_URL = os.getenv('VIRTUOSO_URL', 'http://localhost:8890/sparql')
VIRTUOSO_USER = os.getenv('VIRTUOSO_USER', 'dba')
VIRTUOSO_PASSWORD = os.getenv('VIRTUOSO_DBA_PASSWORD', 'dba')

# Output Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'result.nt')

# SQL Scripts
SQL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'sql')
NORMALIZE_SCHEMA_SQL = os.path.join(SQL_DIR, 'normalize_schema.sql')

# Ontology
ONTOLOGY_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ontology')
ONTOLOGY_FILE = os.path.join(ONTOLOGY_DIR, 'ontoExhibit.rdf')

# Geonames
URI_GEONAMES = "https://www.geonames.org"

# Banned list for filtering invalid data
BANNED_LIST = [
    "CASI",
    "COMPLETADA",
    "GaleríaInforme",
    "Cofradía",
    "Contemporánea",
    "REL",
    "NR",
]
