from pydantic import BaseModel, Field

class AirportResponse(BaseModel):
    airport_id: str = Field(..., alias="Airport ID", description="Unique identifier for the airport")
    name: str = Field(..., alias="Name", description="Name of the airport")
    city: str = Field(..., alias="City", description="City where the airport is located")
    country: str = Field(..., alias="Country", description="Country where the airport is located")
    iata: str = Field(..., alias="IATA", description="IATA code of the airport")
    icao: str = Field(..., alias="ICAO", description="ICAO code of the airport")
    latitude: float = Field(..., alias="Latitude", description="Latitude of the airport location")
    longitude: float = Field(..., alias="Longitude", description="Longitude of the airport location")
    altitude: int = Field(..., alias="Altitude", description="Altitude of the airport in feet")
    timezone: str = Field(..., alias="Timezone", description="Timezone of the airport location")
    dst: str = Field(..., alias="DST", description="Daylight savings time (Y/N)")
    tz_database: str = Field(..., alias="Tz database time zone", description="Time zone database")
    type: str = Field(..., alias="Type", description="Type of airport (e.g., large, medium, small)")
    source: str = Field(..., alias="Source", description="Source of the airport data")

    class Config:
        allow_population_by_field_name = True
