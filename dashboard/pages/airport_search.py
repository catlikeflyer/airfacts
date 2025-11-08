import streamlit as st
import pandas as pd
import plotly.express as px
from database_connector import Neo4jConnector


def show(db: Neo4jConnector):
    """Airport search page"""

    st.title("🔍 Airport Search")
    st.markdown("Search for airports worldwide by name, city, country, or IATA code")

    # Search input
    col1, col2 = st.columns([3, 1])

    with col1:
        search_term = st.text_input(
            "Search",
            placeholder="e.g., JFK, London, United States...",
            help="Enter airport name, city, country, or IATA code",
        )

    with col2:
        search_limit = st.selectbox("Results limit", [10, 25, 50, 100], index=2)

    if search_term:
        # Search airports
        results = db.search_airports(search_term, limit=search_limit)

        if results:
            st.success(f"Found {len(results)} airport(s)")

            # Convert to DataFrame for better display
            df = pd.DataFrame(results)

            # Display results in an interactive table
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "IATA": st.column_config.TextColumn("IATA", width="small"),
                    "Name": st.column_config.TextColumn("Airport Name", width="large"),
                    "City": st.column_config.TextColumn("City", width="medium"),
                    "Country": st.column_config.TextColumn("Country", width="medium"),
                    "Latitude": st.column_config.NumberColumn(
                        "Latitude", format="%.4f"
                    ),
                    "Longitude": st.column_config.NumberColumn(
                        "Longitude", format="%.4f"
                    ),
                    "Altitude": st.column_config.NumberColumn(
                        "Altitude (ft)", format="%d"
                    ),
                },
            )

            # Select an airport for details
            st.markdown("---")
            st.subheader("View Airport Details")

            airport_options = {
                f"{row['IATA']} - {row['Name']} ({row['City']}, {row['Country']})": row[
                    "IATA"
                ]
                for row in results
            }

            selected = st.selectbox(
                "Select an airport to view details",
                options=list(airport_options.keys()),
                key="airport_select",
            )

            if selected:
                iata = airport_options[selected]
                show_airport_details(db, iata)

        else:
            st.warning("No airports found. Try a different search term.")
    else:
        # Show example searches
        st.info("💡 **Try searching for:**")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("🗽 JFK"):
                st.session_state.search_example = "JFK"
                st.rerun()

        with col2:
            if st.button("🇬🇧 London"):
                st.session_state.search_example = "London"
                st.rerun()

        with col3:
            if st.button("🇯🇵 Tokyo"):
                st.session_state.search_example = "Tokyo"
                st.rerun()

        with col4:
            if st.button("🇫🇷 Paris"):
                st.session_state.search_example = "Paris"
                st.rerun()

        # Show some popular airports
        st.markdown("---")
        st.subheader("🌟 Popular Airports")

        popular_airports = ["JFK", "LAX", "LHR", "CDG", "HND", "DXB", "SIN", "FRA"]
        popular_data = []

        for iata in popular_airports:
            airport = db.get_airport_by_iata(iata)
            if airport:
                popular_data.append(airport)

        if popular_data:
            df_popular = pd.DataFrame(popular_data)
            st.dataframe(
                df_popular[["IATA", "Name", "City", "Country"]],
                use_container_width=True,
                hide_index=True,
            )


def show_airport_details(db: Neo4jConnector, iata: str):
    """Display detailed information about a specific airport"""

    airport = db.get_airport_by_iata(iata)

    if not airport:
        st.error(f"Airport {iata} not found")
        return

    # Airport details in columns
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("IATA Code", airport.get("IATA", "N/A"))
        st.metric("ICAO Code", airport.get("ICAO", "N/A"))
        st.metric(
            "Type", airport.get("Type", "N/A").title() if airport.get("Type") else "N/A"
        )

    with col2:
        st.metric("City", airport.get("City", "N/A"))
        st.metric("Country", airport.get("Country", "N/A"))
        st.metric("Timezone", airport.get("Timezone", "N/A"))

    with col3:
        lat = airport.get("Latitude")
        lon = airport.get("Longitude")
        alt = airport.get("Altitude")

        st.metric("Latitude", f"{lat:.4f}" if lat else "N/A")
        st.metric("Longitude", f"{lon:.4f}" if lon else "N/A")
        st.metric("Altitude", f"{alt} ft" if alt else "N/A")

    # Airport name
    st.markdown(f"### {airport.get('Name', 'Unknown Airport')}")

    # Map visualization if coordinates available
    if lat and lon:
        st.markdown("#### 📍 Location")

        map_data = pd.DataFrame(
            [
                {
                    "lat": float(lat),
                    "lon": float(lon),
                    "name": airport.get("Name", ""),
                    "city": airport.get("City", ""),
                }
            ]
        )

        fig = px.scatter_mapbox(
            map_data,
            lat="lat",
            lon="lon",
            hover_name="name",
            hover_data={"lat": False, "lon": False, "city": True},
            zoom=8,
            height=400,
        )

        fig.update_layout(
            mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        st.plotly_chart(fig, use_container_width=True)

    # Routes from this airport
    st.markdown("#### ✈️ Routes")
    routes = db.get_routes_from_airport(iata, limit=50)

    if routes:
        st.info(f"Showing first {min(len(routes), 50)} routes from {iata}")
        df_routes = pd.DataFrame(routes)

        st.dataframe(
            df_routes[
                ["destination", "dest_city", "dest_country", "airline", "distance"]
            ],
            use_container_width=True,
            hide_index=True,
            column_config={
                "destination": "Destination",
                "dest_city": "City",
                "dest_country": "Country",
                "airline": "Airline",
                "distance": st.column_config.NumberColumn(
                    "Distance (km)", format="%.0f"
                ),
            },
        )
    else:
        st.info(f"No route data available for {iata}")
