from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import chat
from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create the FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Mount static files (for the chat UI)
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app/static")
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")


@app.get("/health")
async def health_check():
    """Health check endpoint to verify the service is running."""
    return {"status": "ok"}


# This will be run if you execute the file directly (python main.py)
if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment variable, or use 8000 as default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application with Uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)