import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database_connector import Neo4jConnector


def show(db: Neo4jConnector):
    """Route explorer page"""

    st.title("🗺️ Route Explorer")
    st.markdown("Find and visualize flight routes between airports")

    # Two input methods: tabs
    tab1, tab2 = st.tabs(["✈️ Find Route", "🗺️ View All Airports"])

    with tab1:
        show_route_finder(db)

    with tab2:
        show_airport_map(db)


def show_route_finder(db: Neo4jConnector):
    """Route finding interface"""

    st.subheader("Find Routes Between Airports")

    col1, col2 = st.columns(2)

    with col1:
        source_iata = st.text_input(
            "Source Airport (IATA)",
            placeholder="e.g., JFK",
            help="Enter 3-letter IATA code",
            max_chars=3,
        ).upper()

        if source_iata and len(source_iata) == 3:
            source_info = db.get_airport_by_iata(source_iata)
            if source_info:
                st.success(
                    f"✓ {source_info['Name']} ({source_info['City']}, {source_info['Country']})"
                )
            else:
                st.error(f"Airport {source_iata} not found")

    with col2:
        dest_iata = st.text_input(
            "Destination Airport (IATA)",
            placeholder="e.g., LAX",
            help="Enter 3-letter IATA code",
            max_chars=3,
        ).upper()

        if dest_iata and len(dest_iata) == 3:
            dest_info = db.get_airport_by_iata(dest_iata)
            if dest_info:
                st.success(
                    f"✓ {dest_info['Name']} ({dest_info['City']}, {dest_info['Country']})"
                )
            else:
                st.error(f"Airport {dest_iata} not found")

    # Search button
    if st.button("🔍 Find Routes", type="primary", width="stretch"):
        if source_iata and dest_iata and len(source_iata) == 3 and len(dest_iata) == 3:
            find_and_display_routes(db, source_iata, dest_iata)
        else:
            st.warning("Please enter valid IATA codes for both airports")

    # Quick examples
    st.markdown("---")
    st.markdown("**💡 Popular Routes:**")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("🗽 JFK → LAX 🌴"):
            find_and_display_routes(db, "JFK", "LAX")

    with col2:
        if st.button("🇬🇧 LHR → JFK 🗽"):
            find_and_display_routes(db, "LHR", "JFK")

    with col3:
        if st.button("🇯🇵 NRT → SIN 🇸🇬"):
            find_and_display_routes(db, "NRT", "SIN")

    with col4:
        if st.button("🇦🇪 DXB → LHR 🇬🇧"):
            find_and_display_routes(db, "DXB", "LHR")


def find_and_display_routes(db: Neo4jConnector, source: str, destination: str):
    """Find and display routes between two airports"""

    st.markdown("---")
    st.subheader(f"Routes: {source} → {destination}")

    routes = db.get_routes_between_airports(source, destination)

    if routes:
        st.success(f"Found {len(routes)} route(s)")

        # Display routes in a table
        df = pd.DataFrame(routes)

        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "source": "From",
                "source_name": "Airport",
                "destination": "To",
                "dest_name": "Airport",
                "airline": "Airline",
                "distance": st.column_config.NumberColumn(
                    "Distance (km)", format="%.0f"
                ),
                "stops": "Stops",
                "equipment": "Aircraft",
            },
        )

        # Visualize route on map
        route_coords = db.get_route_with_coordinates(source, destination)

        if route_coords:
            st.markdown("#### 📍 Route Map")
            visualize_route(route_coords)

    else:
        st.warning(f"No direct routes found between {source} and {destination}")
        st.info(
            "💡 Try searching for routes from each airport individually to find connecting flights"
        )


def visualize_route(route_data):
    """Visualize a route on a map"""

    # Create line between airports
    fig = go.Figure()

    # Add route line
    fig.add_trace(
        go.Scattermapbox(
            lon=[route_data["source_lon"], route_data["dest_lon"]],
            lat=[route_data["source_lat"], route_data["dest_lat"]],
            mode="lines",
            line=dict(width=2, color="red"),
            name="Route",
        )
    )

    # Add source airport marker
    fig.add_trace(
        go.Scattermapbox(
            lon=[route_data["source_lon"]],
            lat=[route_data["source_lat"]],
            mode="markers",
            marker=dict(size=12, color="green"),
            text=[f"{route_data['source_iata']}<br>{route_data['source_name']}"],
            name="Source",
        )
    )

    # Add destination airport marker
    fig.add_trace(
        go.Scattermapbox(
            lon=[route_data["dest_lon"]],
            lat=[route_data["dest_lat"]],
            mode="markers",
            marker=dict(size=12, color="blue"),
            text=[f"{route_data['dest_iata']}<br>{route_data['dest_name']}"],
            name="Destination",
        )
    )

    # Calculate center point
    center_lat = (route_data["source_lat"] + route_data["dest_lat"]) / 2
    center_lon = (route_data["source_lon"] + route_data["dest_lon"]) / 2

    fig.update_layout(
        mapbox=dict(
            style="open-street-map", center=dict(lat=center_lat, lon=center_lon), zoom=2
        ),
        showlegend=True,
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )

    st.plotly_chart(fig, width="stretch")

    # Route statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Distance",
            f"{route_data['distance']:.0f} km" if route_data.get("distance") else "N/A",
        )

    with col2:
        st.metric("Airlines", route_data.get("airline", "N/A"))

    with col3:
        distance_miles = (
            route_data["distance"] * 0.621371 if route_data.get("distance") else None
        )
        st.metric(
            "Distance (miles)", f"{distance_miles:.0f} mi" if distance_miles else "N/A"
        )


def show_airport_map(db: Neo4jConnector):
    """Show all airports on a map"""

    st.subheader("Global Airport Map")
    st.info("Displaying up to 5,000 airports worldwide")

    # Filters
    col1, col2 = st.columns(2)

    with col1:
        countries = db.get_all_countries()
        selected_country = st.selectbox(
            "Filter by Country (optional)",
            options=["All Countries"] + countries,
            index=0,
        )

    with col2:
        map_limit = st.slider("Number of airports to display", 100, 5000, 1000, 100)

    # Get airport data
    if selected_country and selected_country != "All Countries":
        airports = db.get_airports_by_country(selected_country, limit=map_limit)
    else:
        airports = db.get_all_airports_for_map(limit=map_limit)

    if airports:
        df = pd.DataFrame(airports)

        st.success(f"Displaying {len(df)} airports")

        # Create map
        fig = px.scatter_mapbox(
            df,
            lat="Latitude",
            lon="Longitude",
            hover_name="Name",
            hover_data={
                "IATA": True,
                "City": True,
                "Country": True,
                "Latitude": False,
                "Longitude": False,
            },
            color="Country",
            zoom=1,
            height=600,
        )

        fig.update_layout(
            mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0}
        )

        st.plotly_chart(fig, width="stretch")

        # Show data table
        with st.expander("📋 View Airport Data"):
            st.dataframe(
                df[["IATA", "Name", "City", "Country"]],
                width="stretch",
                hide_index=True,
            )
    else:
        st.warning("No airports found with the selected filters")
