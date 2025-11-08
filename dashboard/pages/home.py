import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from database_connector import Neo4jConnector


def show(db: Neo4jConnector):
    """Home page with overview statistics and welcome message"""

    # Header
    st.markdown(
        '<div class="main-header">✈️ Airfacts Dashboard</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="sub-header">Explore Global Aviation Data from OpenFlights</div>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # Statistics
    st.subheader("📊 Database Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_airports = db.get_total_airports()
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{total_airports:,}</div>'
            f'<div class="stat-label">Airports</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with col2:
        total_airlines = db.get_total_airlines()
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{total_airlines:,}</div>'
            f'<div class="stat-label">Airlines</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with col3:
        total_routes = db.get_total_routes()
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{total_routes:,}</div>'
            f'<div class="stat-label">Routes</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    with col4:
        total_countries = db.get_total_countries()
        st.markdown(
            f'<div class="stat-box">'
            f'<div class="stat-number">{total_countries:,}</div>'
            f'<div class="stat-label">Countries</div>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Two column layout for visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🌍 Top Countries by Airport Count")
        countries_data = db.get_countries_by_airport_count(limit=10)

        if countries_data:
            fig = px.bar(
                countries_data,
                x="airport_count",
                y="country",
                orientation="h",
                labels={"airport_count": "Number of Airports", "country": "Country"},
                color="airport_count",
                color_continuous_scale="Blues",
            )
            fig.update_layout(
                showlegend=False, height=400, yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No data available")

    with col2:
        st.subheader("🛫 Top Airports by Route Count")
        airports_data = db.get_top_airports_by_routes(limit=10)

        if airports_data:
            fig = px.bar(
                airports_data,
                x="route_count",
                y="IATA",
                orientation="h",
                labels={"route_count": "Number of Routes", "IATA": "Airport"},
                color="route_count",
                color_continuous_scale="Oranges",
                hover_data=["Name", "City", "Country"],
            )
            fig.update_layout(
                showlegend=False, height=400, yaxis={"categoryorder": "total ascending"}
            )
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No data available")

    st.markdown("---")

    # Quick start guide
    st.subheader("🚀 Quick Start Guide")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🔍 Airport Search")
        st.write(
            "Search for airports by name, city, country, or IATA code. View detailed information including coordinates and timezone."
        )

    with col2:
        st.markdown("### 🗺️ Route Explorer")
        st.write(
            "Find routes between airports, visualize connections on a map, and see distance calculations."
        )

    with col3:
        st.markdown("### 📊 Analytics")
        st.write(
            "Explore aviation data through interactive charts and statistics about airports, airlines, and routes."
        )

    st.markdown("---")

    # About section
    with st.expander("ℹ️ About This Dashboard"):
        st.markdown(
            """
        **Airfacts Dashboard** provides an interactive interface to explore global aviation data.
        
        **Data Source:** [OpenFlights](https://openflights.org/data.html)
        
        **Technology Stack:**
        - Frontend: Streamlit
        - Database: Neo4j (Graph Database)
        - Visualization: Plotly
        
        Navigate using the sidebar to explore different features!
        """
        )

    # Development Roadmap
    with st.expander("🗺️ Development Roadmap"):
        st.markdown(
            """
        ### Phase 1 (MVP) ✅ Complete
        - ✅ Airport search and details
        - ✅ Simple route finder between two airports
        - ✅ Basic statistics (total airports, airlines, routes)
        - ✅ Map with all airports plotted
        
        ### Phase 2 🚧 Work in Progress
        - ✅ Airline route networks on map
        - ✅ Top N airports/airlines charts
        - 🚧 Distance-based filtering
        - 🚧 Graph visualization
        
        ### Phase 3 📋 Planned
        - 📋 Shortest path algorithm visualization
        - 📋 Advanced analytics
        - 📋 Export functionality
        - 📋 Real-time filtering
        """
        )
