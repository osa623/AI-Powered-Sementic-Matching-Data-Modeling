from fastapi import FastAPI
from app.api import routes
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

# Include API Routes
app.include_router(routes.router)

@app.get("/")
def health_check():
    return {"status": "online", "module": "Semantic & Data Modeling"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)