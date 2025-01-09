MATCH (source:Airport {IATA: $`Source airport`}), (destination:Airport {IATA: $`Destination airport`})
    MATCH (airline:Airline {IATA: $Airline})
    MERGE (source)-[r:ROUTE]->(destination)
    SET r.Stops = toInteger($Stops),
        r.Equipment = $Equipment,
        r.Codeshare = $Codeshare
    MERGE (airline)-[:OPERATES]->(r);