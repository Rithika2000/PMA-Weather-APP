from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .db import Base, engine
from .routers import weather, records, integrations

app = FastAPI(title="Weather Backend (Tech Assessment 2)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic root + health endpoints
@app.get("/", tags=["root"])
def root():
    return {"message": "Weather backend. See /docs for API endpoints."}

@app.get("/health", tags=["root"])
def health():
    return {"status": "ok"}

# Routers
app.include_router(weather.router)
app.include_router(records.router)
app.include_router(integrations.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
