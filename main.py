from fastapi import FastAPI
from app.api import students_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SurfPlanner API", description="API for surf and tide planning", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://surfplanner-frontend"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(students_router.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
