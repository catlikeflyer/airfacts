LOAD CSV WITH HEADERS FROM 'file:///routes_with_distances.csv' AS row
MATCH (source:Airport {IATA: row.`Source airport`}),
      (destination:Airport {IATA: row.`Destination airport`}),
      (source)-[r:ROUTE {Airline: row.Airline}]->(destination)
SET r.Distance = toFloat(row.Distance);