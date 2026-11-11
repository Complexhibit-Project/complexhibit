
import asyncio
import sys
import os

# Add parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.sparql_client import SparqlClient
from app.core.config import settings

async def fix_genders():
    client = SparqlClient()
    
    print("Checking current gender values...")
    check_query = """
        PREFIX oe: <https://w3id.org/OntoExhibit#>
        SELECT DISTINCT ?g WHERE { ?s oe:gender ?g }
    """
    try:
        result = await client.query(check_query)
        bindings = result.get('results', {}).get('bindings', [])
        values = [b['g']['value'] for b in bindings]
        print(f"Current genders found: {values}")
    except Exception as e:
        print(f"Error checking genders: {e}")
        return

    # Update Male -> Masculino
    print("\nUpdating Male -> Masculino...")
    update_male = """
        PREFIX oe: <https://w3id.org/OntoExhibit#>
        DELETE { ?s oe:gender "Male" }
        INSERT { ?s oe:gender "Masculino" }
        WHERE { ?s oe:gender "Male" }
    """
    try:
        await client.update(update_male)
        print("Update Male -> Masculino executed.")
    except Exception as e:
        print(f"Error updating Male: {e}")

    # Update Female -> Femenino
    print("\nUpdating Female -> Femenino...")
    update_female = """
        PREFIX oe: <https://w3id.org/OntoExhibit#>
        DELETE { ?s oe:gender "Female" }
        INSERT { ?s oe:gender "Femenino" }
        WHERE { ?s oe:gender "Female" }
    """
    try:
        await client.update(update_female)
        print("Update Female -> Femenino executed.")
    except Exception as e:
        print(f"Error updating Female: {e}")

    # Verify results
    print("\nVerifying updates...")
    try:
        result = await client.query(check_query)
        bindings = result.get('results', {}).get('bindings', [])
        values = [b['g']['value'] for b in bindings]
        print(f"New genders found: {values}")
    except Exception as e:
        print(f"Error verifying: {e}")

if __name__ == "__main__":
    asyncio.run(fix_genders())
