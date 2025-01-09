MERGE (airline:Airline {IATA: $IATA})
    SET airline.AirlineID = toInteger($`Airline ID`),
        airline.Name = $Name,
        airline.Alias = $Alias,
        airline.ICAO = $ICAO,
        airline.Callsign = $Callsign,
        airline.Country = $Country,
        airline.Active = $Active;