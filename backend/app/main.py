"""
Main application file for the TripHelix backend API.
This file serves as the entry point for the FastAPI application and sets up all necessary configurations.
"""

# Import necessary FastAPI components and utilities
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from typing import AsyncGenerator

# Import routers from the API endpoints
from app.api.endpoints import chat

# Initialize the FastAPI application with metadata
# This creates the main application instance with title, description, and version information
app = FastAPI(
    title="TripHelix API",  # API title for documentation
    description="AI-powered travel assistant API",  # API description
    version="0.1.0"  # API version
)

# Configure Cross-Origin Resource Sharing (CORS)
# This middleware allows the frontend application to make requests to the backend
# In production, the allow_origins should be restricted to specific frontend URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URLs
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include the chat router with a prefix and tags for API documentation
# This mounts the chat endpoints under the /api/v1 path
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])

# Root endpoint - serves as a welcome message
# This endpoint returns a simple JSON response when accessing the root URL
@app.get("/")
async def root():
    return {"message": "Welcome to TripHelix API"}

# Health check endpoint - used for monitoring and load balancing
# This endpoint allows external services to check if the API is running properly
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Example Server-Sent Events (SSE) generator
# This demonstrates how we'll stream AI responses to the frontend
# In production, this will be replaced with actual AI response streaming
async def generate_stream() -> AsyncGenerator[str, None]:
    """
    Generator function that yields messages for Server-Sent Events (SSE).
    This is a demonstration of how the API will stream AI responses token by token.
    
    Returns:
        AsyncGenerator[str, None]: A generator that yields SSE-formatted messages
    """
    for i in range(5):
        await asyncio.sleep(1)  # Simulate processing time
        yield f"data: Message {i}\n\n"  # SSE format: "data: message\n\n"

# SSE endpoint for streaming responses
# This endpoint allows the frontend to receive real-time updates from the backend
@app.get("/stream")
async def stream():
    """
    Endpoint that returns a streaming response using Server-Sent Events.
    The frontend can connect to this endpoint to receive real-time updates.
    
    Returns:
        StreamingResponse: A response that streams data to the client
    """
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"  # Required for SSE
    )
