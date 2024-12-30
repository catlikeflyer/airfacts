from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import airports  # Import your routers

# Create the FastAPI app
app = FastAPI(
    title="Airfacts API",
    description="API to retrieve information about airports from a CSV file.",
    version="1.0.0",
)

# CORS configuration (optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers
app.include_router(airports.router)

# Root endpoint
@app.get("/")
def read_root():
    """
    Root endpoint to test if the API is running.
    """
    return {"message": "Welcome to the Airport API!"}
