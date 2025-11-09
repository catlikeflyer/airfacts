MATCH
  (source:Airport {IATA: $`Source airport`}),
  (destination:Airport {IATA: $`Destination airport`}),
  (airline:Airline {IATA: $Airline})
MERGE
  (source)-[r:ROUTE {Airline: $Airline, Destination: $`Destination airport`}]->
  (destination)
  ON CREATE SET
    r.Stops = toInteger($Stops),
    r.Equipment = $Equipment,
    r.Codeshare = $Codeshare,
    r.Distance = toFloat($Distance)
  ON MATCH SET
    r.Stops = coalesce(r.Stops, toInteger($Stops)),
    r.Equipment = coalesce(r.Equipment, $Equipment),
    r.Codeshare = coalesce(r.Codeshare, $Codeshare),
    r.Distance = coalesce(r.Distance, toFloat($Distance));