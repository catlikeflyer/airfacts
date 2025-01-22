from fastapi import APIRouter, HTTPException, Query
from database import get_db_session

router = APIRouter()

# Return all airports (default limit 50)
@router.get("/")
def get_all_airports(limit: int = Query(default=50, ge=1)):
    query = """
    MATCH (a:Airport)
    RETURN a.IATA AS IATA, a.Name AS Name, a.City AS City, a.Country AS Country
    LIMIT $limit
    """
    with get_db_session() as session:
        result = session.run(query, limit=limit)
        return [record.data() for record in result]

# Return airport by IATA
@router.get("/{iata}")
def get_airport_by_iata(iata: str):
    '''
    Convert iata to uppercase
    '''
    iata = iata.upper()
    query = """
    MATCH (a:Airport {IATA: $iata})
    RETURN a.IATA AS IATA, a.Name AS Name, a.City AS City, a.Country AS Country
    """
    with get_db_session() as session:
        result = session.run(query, iata=iata).single()
        if not result:
            raise HTTPException(status_code=404, detail="Airport not found")
        return result.data()

# Return all airports in a country
@router.get("/country/{country}", )
def get_airports_by_country(country: str, limit: int = Query(default=50, ge=1)):
    query = """
    MATCH (a:Airport {Country: $country})
    RETURN a.IATA AS IATA, a.Name AS Name, a.City AS City, a.Country AS Country
    """
    with get_db_session() as session:
        result = session.run(query, country=country)
        return [record.data() for record in result]
