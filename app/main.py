import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.api.routes import router

app = FastAPI(
    title="HI-NEXUS Clinical Portal",
    description="Domain-Driven Design (DDD) Pediatric Hyperinsulinism Interpretation Core",
    version="9.0.0"
)

# Register the clean API routes
app.include_rule = False # FastAPI standard
app.include_router(router, prefix="/api")

# Mirror endpoints to root namespace to maintain backwards compatibility
app.include_router(router)

@app.get("/")
def root():
    """
    Serves the premium single-page visual dashboard.
    """
    template_path = os.path.join(os.path.dirname(__file__), "api", "templates", "index.html")
    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return {
        "status": "HI-NEXUS Domain Engine Live",
        "error": "HTML template not found at default location"
    }
