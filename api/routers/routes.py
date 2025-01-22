from fastapi import APIRouter, HTTPException, Query
from database import get_db_session

router = APIRouter()

# Return routes by source airport


@router.get("/source/{source_iata}")
def get_routes_by_source(source_iata: str, limit: int = Query(default=50, ge=1)):
    """
    Returns all routes from a source airport. Orders by distance.

    Args:
        source_iata (str): IATA code of the source airport
        limit (int): Maximum number of routes to return
    """
    source_iata = source_iata.upper()
    query = """
    MATCH (a:Airport {IATA: $source_iata})-[r:ROUTE]->(b:Airport)
    RETURN a.IATA AS source, b.IATA AS destination, r.Airline AS airline, r.Distance AS distance
    ORDER BY r.Distance
    """
    with get_db_session() as session:
        result = session.run(query, source_iata=source_iata)
        return [record.data() for record in result]

# Return routes by destination airport
@router.get("/destination/{destination_iata}")
def get_routes_by_destination(destination_iata: str, limit: int = Query(default=50, ge=1)):
    """
    Returns all routes to a destination airport. Orders by distance.

    Args:
        destination_iata (str): IATA code of the destination airport
        limit (int): Maximum number of routes to return
    """
    destination_iata = destination_iata.upper()
    query = """
    MATCH (a:Airport)-[r:ROUTE]->(b:Airport {IATA: $destination_iata})
    RETURN a.IATA AS source, b.IATA AS destination, r.Airline AS airline, r.Distance AS distance
    ORDER BY r.Distance
    """
    with get_db_session() as session:
        result = session.run(query, destination_iata=destination_iata)
        return [record.data() for record in result]

# Return routes by source and destination
@router.get("/source/{source_iata}/destination/{destination_iata}")
def get_routes_by_source_and_destination(source_iata: str, destination_iata: str):
    """
    Returns all routes from a source airport to a destination airport. Orders by distance.

    Args:
        source_iata (str): IATA code of the source airport
        destination_iata (str): IATA code of the destination airport
    """
    source_iata = source_iata.upper()
    destination_iata = destination_iata.upper()
    query = """
    MATCH (a:Airport {IATA: $source_iata})-[r:ROUTE]->(b:Airport {IATA: $destination_iata})
    RETURN a.IATA AS source, b.IATA AS destination, r.Airline AS airline, r.Distance AS distance
    ORDER BY r.Distance
    """
    with get_db_session() as session:
        result = session.run(query, source_iata=source_iata,
                             destination_iata=destination_iata)
        return [record.data() for record in result]

# Return routes by airline


@router.get("/airline/{airline_iata}")
def get_routes_by_airline(airline_iata: str):
    """
    Returns all routes by an airline. Orders by distance.
    
    Args:
        airline_iata (str): IATA code of the airline
    """
    airline_iata = airline_iata.upper()
    query = """
    MATCH (a:Airport)-[r:ROUTE {Airline: $airline_iata}]->(b:Airport)
    RETURN a.IATA AS source, b.IATA AS destination, r.Airline AS airline, r.Distance AS distance
    ORDER BY r.Distance
    """
    with get_db_session() as session:
        result = session.run(query, airline_iata=airline_iata)
        return [record.data() for record in result]
