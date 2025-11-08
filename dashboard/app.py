import streamlit as st
from database_connector import Neo4jConnector
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Airfacts Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Initialize database connection
@st.cache_resource
def get_db_connector():
    return Neo4jConnector()


# Custom CSS
st.markdown(
    """
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
    }
    .stat-label {
        font-size: 1rem;
        color: #666;
        margin-top: 5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar navigation
st.sidebar.title("🛫 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["🏠 Home", "🔍 Airport Search", "🗺️ Route Explorer", "📊 Analytics"],
    index=0,  # Default to Home page
)

# Initialize connector
db = get_db_connector()

# Page routing
if page == "🏠 Home":
    from pages import home

    home.show(db)
elif page == "🔍 Airport Search":
    from pages import airport_search

    airport_search.show(db)
elif page == "🗺️ Route Explorer":
    from pages import route_explorer

    route_explorer.show(db)
elif page == "📊 Analytics":
    from pages import analytics

    analytics.show(db)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    "**Airfacts Dashboard**\n\n"
    "Explore global aviation data from OpenFlights.\n\n"
    "Data includes airports, airlines, and routes worldwide."
)
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit & Neo4j by DHNAM")
