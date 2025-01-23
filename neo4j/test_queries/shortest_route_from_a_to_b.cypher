MATCH (a:Airport {IATA: 'JFK'})-[:ROUTE*]->(b:Airport {IATA: 'LAX'})
WITH a, b, REDUCE(total_distance = 0, r IN RELATIONSHIPS(p) | total_distance + r.distance) AS total_distance, p
ORDER BY total_distance ASC
RETURN a.IATA AS From, b.IATA AS To, total_distance, nodes(p) AS Stops
LIMIT 1