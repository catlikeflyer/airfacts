MATCH (al:Airline {Country: 'United States'})
RETURN al.IATA AS Code, al.Name AS Name
ORDER BY al.Name