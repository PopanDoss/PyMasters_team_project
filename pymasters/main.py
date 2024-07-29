from fastapi import FastAPI, Request, status, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from pymasters.routes.users import router as users_router
from pymasters.routes.photos import router as photos_router 
from pymasters.routes.comments import router as comments_router

app = FastAPI()

# Include routers for different routes
app.include_router(users_router, prefix='/api')
app.include_router(photos_router, prefix='/api')  # Adds the router for photo-related routes
app.include_router(comments_router, prefix='/api')  # Adds the router for comment-related routes

@app.get("/")
def read_root():
    """
    Root endpoint to test API availability.

    Returns:
    - A JSON response with a message indicating the API is available.
    """
    return {"message": "Hello World"}


