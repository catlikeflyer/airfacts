MERGE (a:Airport {IATA: $IATA})
    SET a.AirportID = toInteger($`Airport ID`),
        a.Name = $Name,
        a.City = $City,
        a.Country = $Country,
        a.Latitude = toFloat($Latitude),
        a.Longitude = toFloat($Longitude),
        a.Altitude = toInteger($Altitude),
        a.Timezone = toFloat($Timezone),
        a.DST = $DST,
        a.Tz = $`Tz database time zone`,
        a.Type = $Type,
        a.Source = $Source;