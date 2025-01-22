from fastapi import APIRouter, HTTPException, Query
from database import get_db_session

router = APIRouter()

# Return all airlines
@router.get("/")
def get_all_airlines(limit: int = Query(default=50, ge=1), skip: int = Query(default=0, ge=0)):
    """
    Returns all airlines in the database.

    Args:
        limit (int): Maximum number of airlines to return
        skip (int): Number of airlines to skip
    """
    query = """
    MATCH (a:Airline)
    RETURN a.IATA AS IATA, a.Name AS Name, a.Country AS Country
    """
    with get_db_session() as session:
        result = session.run(query)
        return [record.data() for record in result]

# Return airline by IATA
@router.get("/{iata}")
def get_airline_by_iata(iata: str):
    """
    Returns an airline by IATA code. Converts IATA code to uppercase.

    Args:
        iata (str): IATA code of the airline
    """
    iata = iata.upper()
    query = """
    MATCH (a:Airline {IATA: $iata})
    RETURN a.IATA AS IATA, a.Name AS Name, a.Country AS Country
    """
    with get_db_session() as session:
        result = session.run(query, iata=iata).single()
        if not result:
            raise HTTPException(status_code=404, detail="Airline not found")
        return result.data()

# Return airline by country
@router.get("/country/{country}")
def get_airlines_by_country(country: str, limit: int = Query(default=50, ge=1)):
    """
    Returns all airlines in a country. Capitalizes country name.

    Args:
        country (str): Country name
        limit (int): Maximum number of airlines to return
    """
    country = country.capitalize()
    query = """
    MATCH (a:Airline {Country: $country})
    RETURN a.IATA AS IATA, a.Name AS Name, a.Country AS Country
    """
    with get_db_session() as session:
        result = session.run(query, country=country)
        return [record.data() for record in result]
