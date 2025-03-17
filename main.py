from fastapi import FastAPI
from app.api import router as api_router

app = FastAPI(title="SurfPlanner API", description="API for surf and tide planning", version="1.0")

# Include all routers
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
