import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database_connector import Neo4jConnector


def show(db: Neo4jConnector):
    """Airline explorer page with detailed airline information and network visualization"""

    st.title("✈️ Airline Explorer")
    st.markdown("Explore airlines, their routes, and global network presence")

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🔍 Search", "📊 Analytics", "🗺️ Network", "📈 Comparison"]
    )

    with tab1:
        show_airline_search(db)

    with tab2:
        show_airline_analytics(db)

    with tab3:
        show_airline_network(db)

    with tab4:
        show_airline_comparison(db)


def show_airline_search(db: Neo4jConnector):
    """Search and view detailed airline information"""

    st.subheader("Search Airlines")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_term = st.text_input(
            "Search by airline name, country, or IATA code",
            placeholder="e.g., American, AA, United States",
        )

    with col2:
        search_limit = st.selectbox("Limit", [10, 25, 50, 100], index=1)

    if search_term:
        airlines = db.search_airlines(search_term, limit=search_limit)

        if airlines:
            st.success(f"Found {len(airlines)} airline(s)")

            # Display as selectbox for detailed view
            airline_names = [
                f"{a['IATA']} - {a['Name']} ({a['Country']})" for a in airlines
            ]
            selected = st.selectbox("Select an airline", airline_names)

            if selected:
                airline_iata = selected.split(" - ")[0]
                show_airline_details(db, airline_iata)
        else:
            st.info("No airlines found matching your search")

    st.markdown("---")

    # Browse by country
    st.subheader("Browse Airlines by Country")

    all_countries = sorted(
        set([a["Country"] for a in db.search_airlines("", limit=10000) if a["Country"]])
    )

    if all_countries:
        selected_country = st.selectbox("Select a country", all_countries)

        if selected_country:
            country_airlines = db.get_airlines_by_country(selected_country, limit=100)

            if country_airlines:
                df = pd.DataFrame(country_airlines)
                st.markdown(f"#### Airlines in {selected_country}")
                st.dataframe(
                    df,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "IATA": "Code",
                        "Name": "Airline Name",
                        "Country": "Country",
                        "Callsign": "Callsign",
                        "Active": "Status",
                    },
                )
            else:
                st.info(f"No airlines found for {selected_country}")


def show_airline_details(db: Neo4jConnector, iata: str):
    """Display detailed information about a specific airline"""

    airline_info = db.get_airline_by_iata(iata)

    if not airline_info:
        st.error(f"Airline {iata} not found")
        return

    st.markdown("---")
    st.subheader(f"Airline Details: {airline_info['Name']}")

    # Basic information
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("**IATA Code**")
        st.markdown(f"`{airline_info['IATA']}`")

    with col2:
        st.markdown("**Country**")
        st.write(airline_info["Country"])

    with col3:
        st.markdown("**ICAO Code**")
        st.write(airline_info.get("ICAO", "N/A"))

    with col4:
        st.markdown("**Callsign**")
        st.write(airline_info.get("Callsign", "N/A"))

    st.markdown("---")

    # Route statistics
    st.subheader("🛫 Route Statistics")

    routes_data = db.get_airline_routes(iata, limit=1000)

    if routes_data:
        df_routes = pd.DataFrame(routes_data)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Routes", len(df_routes))

        with col2:
            if "distance" in df_routes.columns and df_routes["distance"].notna().any():
                avg_distance = df_routes["distance"].mean()
                st.metric("Avg Distance", f"{avg_distance:.0f} km")
            else:
                st.metric("Avg Distance", "N/A")

        with col3:
            unique_destinations = df_routes["destination"].nunique()
            st.metric("Unique Destinations", unique_destinations)

        with col4:
            unique_sources = df_routes["source"].nunique()
            st.metric("Hub Airports", unique_sources)

        st.markdown("---")

        # Distance distribution
        if "distance" in df_routes.columns and df_routes["distance"].notna().any():
            st.markdown("#### ✈️ Route Distance Distribution")

            fig_hist = px.histogram(
                df_routes,
                x="distance",
                nbins=30,
                labels={"distance": "Distance (km)", "count": "Number of Routes"},
                title=f"Route Distance Distribution for {iata}",
                color_discrete_sequence=["#1f77b4"],
            )
            fig_hist.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_hist, width="stretch")

            st.markdown("---")

        # Top routes
        st.markdown("#### 🎯 Top Routes by Distance")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Longest Routes**")
            if "distance" in df_routes.columns:
                longest = df_routes.nlargest(10, "distance")
            else:
                longest = df_routes.head(10)

            st.dataframe(
                longest[
                    ["source", "source_name", "destination", "dest_name", "distance"]
                ],
                width="stretch",
                hide_index=True,
                column_config={
                    "source": "From",
                    "source_name": "From Airport",
                    "destination": "To",
                    "dest_name": "To Airport",
                    "distance": st.column_config.NumberColumn(
                        "Distance (km)", format="%.0f"
                    ),
                },
            )

        with col2:
            st.markdown("**Most Frequent Destinations**")
            dest_counts = df_routes["destination"].value_counts().head(10)
            dest_names = (
                df_routes.groupby("destination")["dest_name"]
                .first()
                .reindex(dest_counts.index)
            )

            df_dest = pd.DataFrame(
                {"Destination": dest_counts.index, "Routes": dest_counts.values}
            )

            fig_bar = px.bar(
                df_dest,
                x="Routes",
                y="Destination",
                orientation="h",
                color="Routes",
                color_continuous_scale="Greens",
            )
            fig_bar.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig_bar, width="stretch")

    else:
        st.info(f"No routes found for airline {iata}")


def show_airline_analytics(db: Neo4jConnector):
    """Global airline analytics"""

    st.subheader("Global Airline Analytics")

    col1, col2, col3 = st.columns(3)

    with col1:
        total_airlines = db.get_total_airlines()
        st.metric("Total Airlines", total_airlines)

    with col2:
        status_counts = db.get_airlines_by_active_status()
        active = status_counts.get("Active", 0)
        st.metric("Active Airlines", active)

    with col3:
        inactive = status_counts.get("Inactive", 0)
        st.metric("Inactive Airlines", inactive)

    st.markdown("---")

    # Top airlines by routes
    st.markdown("#### 🏆 Top Airlines by Route Count")

    limit = st.slider("Number of airlines", 5, 50, 15, key="top_airlines_limit")
    top_airlines = db.get_top_airlines_by_routes(limit=limit)

    if top_airlines:
        df_airlines = pd.DataFrame(top_airlines)

        col1, col2 = st.columns(2)

        with col1:
            fig_bar = px.bar(
                df_airlines,
                x="route_count",
                y="IATA",
                orientation="h",
                labels={"route_count": "Number of Routes", "IATA": "Airline Code"},
                color="route_count",
                color_continuous_scale="Blues",
                hover_data=["Name", "Country"],
            )
            fig_bar.update_layout(
                showlegend=False, height=500, yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig_bar, width="stretch")

        with col2:
            # Treemap by country
            fig_tree = px.treemap(
                df_airlines,
                path=["Country", "Name"],
                values="route_count",
                color="route_count",
                color_continuous_scale="RdYlGn",
                hover_data=["IATA"],
                title="Airlines by Country and Route Count",
            )
            fig_tree.update_layout(height=500)
            st.plotly_chart(fig_tree, width="stretch")

        st.markdown("---")

        # Data table
        with st.expander("📋 View Data"):
            st.dataframe(
                df_airlines,
                width="stretch",
                hide_index=True,
                column_config={
                    "IATA": "Code",
                    "Name": "Airline Name",
                    "Country": "Country",
                    "route_count": st.column_config.NumberColumn("Routes", format="%d"),
                },
            )

    else:
        st.info("No airline data available")

    st.markdown("---")

    # Countries with most airlines
    st.markdown("#### 🌍 Countries with Most Airlines")

    countries_limit = st.slider(
        "Number of countries", 5, 30, 15, key="airline_countries"
    )
    countries_data = db.get_countries_by_airline_count(limit=countries_limit)

    if countries_data:
        df_countries = pd.DataFrame(countries_data)

        col1, col2 = st.columns(2)

        with col1:
            fig_bar = px.bar(
                df_countries,
                x="airline_count",
                y="country",
                orientation="h",
                labels={"airline_count": "Number of Airlines", "country": "Country"},
                color="airline_count",
                color_continuous_scale="Purples",
            )
            fig_bar.update_layout(
                showlegend=False, height=500, yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig_bar, width="stretch")

        with col2:
            fig_pie = px.pie(
                df_countries,
                values="airline_count",
                names="country",
                title="Airline Distribution by Country",
            )
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, width="stretch")

    else:
        st.info("No country data available")


def show_airline_network(db: Neo4jConnector):
    """Visualize airline network on a map"""

    st.subheader("Airline Network Visualization")

    st.write("View an airline's route network on a world map")

    airline_iata = st.text_input(
        "Enter airline IATA code",
        placeholder="e.g., AA, BA, LH",
        max_chars=3,
    ).upper()

    if airline_iata and len(airline_iata) == 2:
        airline_info = db.get_airline_by_iata(airline_iata)

        if airline_info:
            st.success(f"✓ {airline_info['Name']} ({airline_info['Country']})")

            # Get network data
            network_data = db.get_airline_network(airline_iata, limit=200)

            if network_data:
                st.info(f"Showing up to 200 routes for {airline_iata}")

                # Create map visualization
                routes_for_map = []

                for route in network_data:
                    routes_for_map.append(
                        {
                            "source_lat": route["source_lat"],
                            "source_lon": route["source_lon"],
                            "dest_lat": route["dest_lat"],
                            "dest_lon": route["dest_lon"],
                            "source": route["source_iata"],
                            "destination": route["dest_iata"],
                            "distance": route.get("distance", 0),
                        }
                    )

                # Create figure with routes
                fig = go.Figure()

                # Add route lines
                for route in routes_for_map:
                    fig.add_trace(
                        go.Scattergeo(
                            lon=[route["source_lon"], route["dest_lon"]],
                            lat=[route["source_lat"], route["dest_lat"]],
                            mode="lines",
                            line=dict(width=0.5, color="rgba(31, 119, 180, 0.3)"),
                            hoverinfo="text",
                            text=f"{route['source']} → {route['destination']}<br>Distance: {route['distance']:.0f} km",
                            showlegend=False,
                        )
                    )

                # Add source airports
                source_coords = {}
                for route in routes_for_map:
                    if route["source"] not in source_coords:
                        source_coords[route["source"]] = (
                            route["source_lat"],
                            route["source_lon"],
                        )

                fig.add_trace(
                    go.Scattergeo(
                        lon=[coord[1] for coord in source_coords.values()],
                        lat=[coord[0] for coord in source_coords.values()],
                        text=[f"Departure: {code}" for code in source_coords.keys()],
                        mode="markers",
                        marker=dict(size=8, color="blue", opacity=0.7),
                        name="Departure Airports",
                        hoverinfo="text",
                    )
                )

                # Add destination airports
                dest_coords = {}
                for route in routes_for_map:
                    if route["destination"] not in dest_coords:
                        dest_coords[route["destination"]] = (
                            route["dest_lat"],
                            route["dest_lon"],
                        )

                fig.add_trace(
                    go.Scattergeo(
                        lon=[coord[1] for coord in dest_coords.values()],
                        lat=[coord[0] for coord in dest_coords.values()],
                        text=[f"Arrival: {code}" for code in dest_coords.keys()],
                        mode="markers",
                        marker=dict(size=6, color="red", opacity=0.7),
                        name="Destination Airports",
                        hoverinfo="text",
                    )
                )

                fig.update_layout(
                    title=f"Route Network for {airline_info['Name']} ({airline_iata})",
                    geo=dict(
                        projection_type="natural earth",
                        showland=True,
                        landcolor="rgb(243, 243, 243)",
                        coastcolor="rgb(204, 204, 204)",
                        countrycolor="rgb(204, 204, 204)",
                        showlakes=True,
                        lakecolor="rgb(220, 240, 255)",
                    ),
                    height=600,
                )

                st.plotly_chart(fig, width="stretch")

                st.markdown("---")

                # Statistics
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Routes Displayed", len(routes_for_map))

                with col2:
                    st.metric("Departure Hubs", len(source_coords))

                with col3:
                    st.metric("Destination Airports", len(dest_coords))

            else:
                st.warning(f"No geographic route data found for airline {airline_iata}")
        else:
            st.error(f"Airline {airline_iata} not found")

    elif airline_iata:
        st.warning("Please enter a valid 2-letter IATA airline code")


def show_airline_comparison(db: Neo4jConnector):
    """Compare multiple airlines"""

    st.subheader("Airline Comparison")

    st.write("Compare up to 5 airlines based on their route networks")

    # Get list of top airlines for quick selection
    top_airlines = db.get_top_airlines_by_routes(limit=50)

    if top_airlines:
        airline_options = {
            f"{a['IATA']} - {a['Name']}": a["IATA"] for a in top_airlines
        }

        selected_airlines = st.multiselect(
            "Select airlines to compare",
            options=list(airline_options.keys()),
            max_selections=5,
        )

        if selected_airlines:
            selected_iatas = [airline_options[a] for a in selected_airlines]

            # Collect data for comparison
            comparison_data = []

            for iata in selected_iatas:
                airline = db.get_airline_by_iata(iata)
                routes = db.get_airline_routes(iata, limit=10000)

                if airline and routes:
                    df_routes = pd.DataFrame(routes)

                    comparison_data.append(
                        {
                            "Airline": airline["Name"],
                            "Code": iata,
                            "Country": airline["Country"],
                            "Total Routes": len(df_routes),
                            "Unique Destinations": df_routes["destination"].nunique(),
                            "Unique Sources": df_routes["source"].nunique(),
                            "Avg Distance": (
                                df_routes["distance"].mean()
                                if "distance" in df_routes.columns
                                and df_routes["distance"].notna().any()
                                else 0
                            ),
                        }
                    )

            if comparison_data:
                df_comparison = pd.DataFrame(comparison_data)

                st.markdown("#### Comparison Table")
                st.dataframe(
                    df_comparison,
                    width="stretch",
                    hide_index=True,
                    column_config={
                        "Airline": "Airline Name",
                        "Code": "IATA",
                        "Country": "Country",
                        "Total Routes": st.column_config.NumberColumn(
                            "Total Routes", format="%d"
                        ),
                        "Unique Destinations": st.column_config.NumberColumn(
                            "Destinations", format="%d"
                        ),
                        "Unique Sources": st.column_config.NumberColumn(
                            "Hub Airports", format="%d"
                        ),
                        "Avg Distance": st.column_config.NumberColumn(
                            "Avg Distance (km)", format="%.0f"
                        ),
                    },
                )

                st.markdown("---")

                # Visualization
                col1, col2 = st.columns(2)

                with col1:
                    fig_routes = px.bar(
                        df_comparison,
                        x="Code",
                        y="Total Routes",
                        title="Total Routes Comparison",
                        color="Total Routes",
                        color_continuous_scale="Blues",
                    )
                    fig_routes.update_layout(height=400)
                    st.plotly_chart(fig_routes, width="stretch")

                with col2:
                    fig_avg = px.bar(
                        df_comparison,
                        x="Code",
                        y="Avg Distance",
                        title="Average Route Distance Comparison",
                        color="Avg Distance",
                        color_continuous_scale="Oranges",
                    )
                    fig_avg.update_layout(height=400)
                    st.plotly_chart(fig_avg, width="stretch")

            else:
                st.warning("Unable to load data for selected airlines")
        else:
            st.info("Select airlines to compare from the list above")
    else:
        st.info("No airline data available for comparison")
