MATCH (a:Airport)
RETURN a.IATA AS Code, a.Name AS Name, a.City AS City, a.Country AS Country
LIMIT 10