from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import airports, airlines, routes
from database import close_db

app = FastAPI(
    title="Airfacts API",
    description="API for Airfacts, a Neo4j-based flight database",
    version="2.0.0",
    contact={
        "name": "Do Hyun Nam",
        "url": "https://dhnam.me",
        "email": "dhnam@aol.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8501",  # Local Streamlit
    "http://127.0.0.1:8501",  # Local Streamlit
    # Add your production URLs here after deployment:
    # "https://airfacts.streamlit.app",
    # "https://airfacts-api.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allowed origins
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(airports.router, prefix="/api/airports", tags=["Airports"])
app.include_router(airlines.router, prefix="/api/airlines", tags=["Airlines"])
app.include_router(routes.router, prefix="/api/routes", tags=["Routes"])


@app.get("/")
async def root():
    return {"message": "Welcome to Airfacts!"}


@app.on_event("shutdown")
def shutdown():
    close_db()
