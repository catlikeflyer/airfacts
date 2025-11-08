import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database_connector import Neo4jConnector


def show(db: Neo4jConnector):
    """Analytics page with various visualizations"""

    st.title("📊 Analytics Dashboard")
    st.markdown("Explore aviation data through interactive visualizations")

    # Tabs for different analytics
    tab1, tab2, tab3 = st.tabs(["🛫 Airports", "✈️ Airlines", "🗺️ Routes"])

    with tab1:
        show_airport_analytics(db)

    with tab2:
        show_airline_analytics(db)

    with tab3:
        show_route_analytics(db)


def show_airport_analytics(db: Neo4jConnector):
    """Airport-related analytics"""

    st.subheader("Airport Analytics")

    # Top airports by routes
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🔝 Top Airports by Route Count")
        limit = st.slider("Number of airports", 5, 25, 10, key="airport_limit")

    top_airports = db.get_top_airports_by_routes(limit=limit)

    if top_airports:
        df = pd.DataFrame(top_airports)

        # Bar chart
        fig = px.bar(
            df,
            x="route_count",
            y="IATA",
            orientation="h",
            labels={"route_count": "Number of Routes", "IATA": "Airport Code"},
            color="route_count",
            color_continuous_scale="Viridis",
            hover_data=["Name", "City", "Country"],
        )
        fig.update_layout(
            showlegend=False, height=400, yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig, width="stretch")

        # Data table
        with st.expander("📋 View Data"):
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "IATA": "Code",
                    "Name": "Airport Name",
                    "City": "City",
                    "Country": "Country",
                    "route_count": st.column_config.NumberColumn("Routes", format="%d"),
                },
            )
    else:
        st.info("No data available")

    st.markdown("---")

    # Countries by airport count
    st.markdown("#### 🌍 Countries by Airport Count")

    countries_limit = st.slider("Number of countries", 5, 30, 15, key="country_limit")
    countries_data = db.get_countries_by_airport_count(limit=countries_limit)

    if countries_data:
        df_countries = pd.DataFrame(countries_data)

        col1, col2 = st.columns(2)

        with col1:
            # Bar chart
            fig_bar = px.bar(
                df_countries,
                x="airport_count",
                y="country",
                orientation="h",
                labels={"airport_count": "Number of Airports", "country": "Country"},
                color="airport_count",
                color_continuous_scale="Blues",
            )
            fig_bar.update_layout(
                showlegend=False, height=500, yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig_bar, width="stretch")

        with col2:
            # Pie chart
            fig_pie = px.pie(
                df_countries,
                values="airport_count",
                names="country",
                title="Airport Distribution",
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            fig_pie.update_layout(height=500)
            st.plotly_chart(fig_pie, width="stretch")


def show_airline_analytics(db: Neo4jConnector):
    """Airline-related analytics"""

    st.subheader("Airline Analytics")

    st.markdown("#### 🔝 Top Airlines by Route Count")

    limit = st.slider("Number of airlines", 5, 25, 10, key="airline_limit")
    top_airlines = db.get_top_airlines_by_routes(limit=limit)

    if top_airlines:
        df = pd.DataFrame(top_airlines)

        # Horizontal bar chart
        fig = px.bar(
            df,
            x="route_count",
            y="IATA",
            orientation="h",
            labels={"route_count": "Number of Routes", "IATA": "Airline Code"},
            color="route_count",
            color_continuous_scale="Oranges",
            hover_data=["Name", "Country"],
        )
        fig.update_layout(
            showlegend=False, height=400, yaxis={"categoryorder": "total ascending"}
        )
        st.plotly_chart(fig, width="stretch")

        # Data table
        with st.expander("📋 View Data"):
            st.dataframe(
                df,
                width="stretch",
                hide_index=True,
                column_config={
                    "IATA": "Code",
                    "Name": "Airline Name",
                    "Country": "Country",
                    "route_count": st.column_config.NumberColumn("Routes", format="%d"),
                },
            )

        # Additional visualization - Treemap
        st.markdown("#### 📊 Airline Market Share (by Route Count)")

        fig_tree = px.treemap(
            df,
            path=["Country", "Name"],
            values="route_count",
            color="route_count",
            color_continuous_scale="RdYlGn",
            hover_data=["IATA"],
        )
        fig_tree.update_layout(height=500)
        st.plotly_chart(fig_tree, width="stretch")

    else:
        st.info("No data available")


def show_route_analytics(db: Neo4jConnector):
    """Route-related analytics"""

    st.subheader("Route Analytics")

    # Summary statistics
    col1, col2, col3 = st.columns(3)

    with col1:
        total_routes = db.get_total_routes()
        st.metric("Total Routes", f"{total_routes:,}")

    with col2:
        total_airports = db.get_total_airports()
        st.metric("Total Airports", f"{total_airports:,}")

    with col3:
        if total_airports > 0:
            avg_routes = total_routes / total_airports
            st.metric("Avg Routes per Airport", f"{avg_routes:.1f}")
        else:
            st.metric("Avg Routes per Airport", "N/A")

    st.markdown("---")

    # Search routes from a specific airport
    st.markdown("#### ✈️ Routes from Airport")

    col1, col2 = st.columns([2, 1])

    with col1:
        airport_iata = st.text_input(
            "Enter airport IATA code",
            placeholder="e.g., JFK",
            max_chars=3,
            key="routes_airport",
        ).upper()

    with col2:
        route_limit = st.selectbox(
            "Limit", [25, 50, 100, 200], index=1, key="route_limit"
        )

    if airport_iata and len(airport_iata) == 3:
        airport_info = db.get_airport_by_iata(airport_iata)

        if airport_info:
            st.success(
                f"✓ {airport_info['Name']} ({airport_info['City']}, {airport_info['Country']})"
            )

            routes = db.get_routes_from_airport(airport_iata, limit=route_limit)

            if routes:
                df_routes = pd.DataFrame(routes)

                st.info(f"Found {len(df_routes)} routes from {airport_iata}")

                # Show distance distribution
                if "distance" in df_routes.columns:
                    fig_hist = px.histogram(
                        df_routes,
                        x="distance",
                        nbins=30,
                        labels={
                            "distance": "Distance (km)",
                            "count": "Number of Routes",
                        },
                        title=f"Route Distance Distribution from {airport_iata}",
                    )
                    fig_hist.update_layout(height=300)
                    st.plotly_chart(fig_hist, width="stretch")

                # Show top destinations
                st.markdown("##### 🎯 Top Destinations by Distance")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Nearest Destinations**")
                    nearest = (
                        df_routes.nsmallest(10, "distance")
                        if "distance" in df_routes.columns
                        else df_routes.head(10)
                    )
                    st.dataframe(
                        nearest[
                            ["destination", "dest_city", "dest_country", "distance"]
                        ],
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "destination": "IATA",
                            "dest_city": "City",
                            "dest_country": "Country",
                            "distance": st.column_config.NumberColumn(
                                "Distance (km)", format="%.0f"
                            ),
                        },
                    )

                with col2:
                    st.markdown("**Farthest Destinations**")
                    farthest = (
                        df_routes.nlargest(10, "distance")
                        if "distance" in df_routes.columns
                        else df_routes.tail(10)
                    )
                    st.dataframe(
                        farthest[
                            ["destination", "dest_city", "dest_country", "distance"]
                        ],
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "destination": "IATA",
                            "dest_city": "City",
                            "dest_country": "Country",
                            "distance": st.column_config.NumberColumn(
                                "Distance (km)", format="%.0f"
                            ),
                        },
                    )

            else:
                st.warning(f"No routes found from {airport_iata}")
        else:
            st.error(f"Airport {airport_iata} not found")
