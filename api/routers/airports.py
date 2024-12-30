from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from schemas.airport import AirportResponse
from utils.csv_loader import load_csv

router = APIRouter(prefix="/airports", tags=["Airports"])

# Load airport data from the CSV file
airport_data = load_csv("../datasets/airports.csv")

@router.get("/", response_model=List[AirportResponse])
def get_airports(
    country: Optional[str] = Query(None, description="Filter airports by country"),
    city: Optional[str] = Query(None, description="Filter airports by city"),
    iata: Optional[str] = Query(None, description="Filter airports by IATA code")
):
    """
    Get a list of all airports with optional filters by country, city, or IATA code.
    """
    results = airport_data

    if country:
        results = [a for a in results if country.lower() in a["Country"].lower()]
    if city:
        results = [a for a in results if city.lower() in a["City"].lower()]
    if iata:
        results = [a for a in results if iata.lower() == a["IATA"].lower()]

    if not results:
        raise HTTPException(status_code=404, detail="No airports found with the given filters.")
    
    return results


@router.get("/{airport_id}", response_model=AirportResponse)
def get_airport_by_id(airport_id: str):
    """
    Get details of a specific airport by its ID.
    """
    airport = next((a for a in airport_data if a["Airport ID"] == airport_id), None)
    if not airport:
        raise HTTPException(status_code=404, detail="Airport not found.")
    return airport
