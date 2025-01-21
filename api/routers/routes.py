from fastapi import APIRouter, HTTPException
from database import get_db_session

router = APIRouter()

# Return routes by source airport
@router.get("/source/{source_iata}")
def get_routes_by_source(source_iata: str):
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
def get_routes_by_destination(destination_iata: str):
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
    query = """
    MATCH (a:Airport {IATA: $source_iata})-[r:ROUTE]->(b:Airport {IATA: $destination_iata})
    RETURN a.IATA AS source, b.IATA AS destination, r.Airline AS airline, r.Distance AS distance
    ORDER BY r.Distance
    """
    with get_db_session() as session:
        result = session.run(query, source_iata=source_iata, destination_iata=destination_iata)
        return [record.data() for record in result]

# Return routes by airline
@router.get("/airline/{airline_iata}")
def get_routes_by_airline(airline_iata: str):
    query = """
    MATCH (a:Airport)-[r:ROUTE {Airline: $airline_iata}]->(b:Airport)
    RETURN a.IATA AS source, b.IATA AS destination, r.Airline AS airline, r.Distance AS distance
    ORDER BY r.Distance
    """
    with get_db_session() as session:
        result = session.run(query, airline_iata=airline_iata)
        return [record.data() for record in result]
