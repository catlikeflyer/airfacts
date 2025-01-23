MATCH (al:Airline {IATA: 'AA'})-[:OPERATES]->(r:ROUTE)
RETURN r.source AS From, r.destination AS To, al.Name AS Airline
