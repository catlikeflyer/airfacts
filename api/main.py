from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import airports, airlines, routes
from database import close_db

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost:3000",  # Frontend or other allowed origins
    "http://127.0.0.1:3000",
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