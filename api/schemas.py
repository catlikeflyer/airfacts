from pydantic import BaseModel, Field
from typing import Optional


class AirportBase(BaseModel):
    """Base schema for Airport"""

    IATA: str = Field(..., description="IATA code of the airport", example="JFK")
    Name: str = Field(
        ...,
        description="Name of the airport",
        example="John F Kennedy International Airport",
    )
    City: str = Field(
        ..., description="City where the airport is located", example="New York"
    )
    Country: str = Field(
        ..., description="Country where the airport is located", example="United States"
    )


class AirportDetail(AirportBase):
    """Detailed schema for Airport with all fields"""

    ICAO: Optional[str] = Field(
        None, description="ICAO code of the airport", example="KJFK"
    )
    Latitude: Optional[float] = Field(
        None, description="Latitude of the airport", example=40.639751
    )
    Longitude: Optional[float] = Field(
        None, description="Longitude of the airport", example=-73.778925
    )
    Altitude: Optional[int] = Field(None, description="Altitude in feet", example=13)
    Timezone: Optional[str] = Field(
        None, description="Hours offset from UTC", example="-5"
    )
    DST: Optional[str] = Field(None, description="Daylight savings time", example="A")
    TzDatabaseTimeZone: Optional[str] = Field(
        None,
        alias="Tz database time zone",
        description="Timezone in Olson format",
        example="America/New_York",
    )
    Type: Optional[str] = Field(None, description="Type of airport", example="airport")
    Source: Optional[str] = Field(
        None, description="Source of the data", example="OurAirports"
    )

    class Config:
        populate_by_name = True


class AirlineBase(BaseModel):
    """Base schema for Airline"""

    IATA: str = Field(..., description="IATA code of the airline", example="AA")
    Name: str = Field(
        ..., description="Name of the airline", example="American Airlines"
    )
    Country: str = Field(
        ..., description="Country where the airline is based", example="United States"
    )


class AirlineDetail(AirlineBase):
    """Detailed schema for Airline with all fields"""

    ICAO: Optional[str] = Field(
        None, description="ICAO code of the airline", example="AAL"
    )
    Callsign: Optional[str] = Field(
        None, description="Airline callsign", example="AMERICAN"
    )
    Alias: Optional[str] = Field(None, description="Alias of the airline")
    Active: Optional[str] = Field(
        None, description="'Y' if airline is active, 'N' if inactive", example="Y"
    )

    class Config:
        populate_by_name = True


class RouteBase(BaseModel):
    """Base schema for Route"""

    source: str = Field(..., description="IATA code of source airport", example="JFK")
    destination: str = Field(
        ..., description="IATA code of destination airport", example="LAX"
    )
    airline: str = Field(
        ..., description="IATA code of airline operating the route", example="AA"
    )
    distance: Optional[float] = Field(
        None, description="Distance in kilometers", example=3983.0
    )


class RouteDetail(RouteBase):
    """Detailed schema for Route with all fields"""

    stops: Optional[int] = Field(
        None, description="Number of stops (0 for direct)", example=0
    )
    equipment: Optional[str] = Field(
        None, description="Aircraft types used on this route", example="737 738 739"
    )
    codeshare: Optional[str] = Field(None, description="Codeshare indicator")

    class Config:
        populate_by_name = True


class ErrorResponse(BaseModel):
    """Standard error response"""

    detail: str = Field(..., description="Error message", example="Airport not found")


class PaginationParams(BaseModel):
    """Pagination parameters"""

    limit: int = Field(
        default=50, ge=1, le=1000, description="Maximum number of items to return"
    )
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
