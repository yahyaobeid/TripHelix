# Import necessary FastAPI components and utilities
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio
from typing import AsyncGenerator

# Initialize the FastAPI application with metadata
app = FastAPI(
    title="TripHelix API",  # API title for documentation
    description="AI-powered travel assistant API",  # API description
    version="0.1.0"  # API version
)

# Configure Cross-Origin Resource Sharing (CORS)
# This allows the frontend to make requests to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URLs
    allow_credentials=True,  # Allow cookies and authentication headers
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Root endpoint - serves as a welcome message
@app.get("/")
async def root():
    return {"message": "Welcome to TripHelix API"}

# Health check endpoint - used for monitoring and load balancing
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Example Server-Sent Events (SSE) generator
# This demonstrates how we'll stream AI responses to the frontend
async def generate_stream() -> AsyncGenerator[str, None]:
    """
    Generator function that yields messages for SSE.
    In production, this will stream AI responses token by token.
    """
    for i in range(5):
        await asyncio.sleep(1)  # Simulate processing time
        yield f"data: Message {i}\n\n"  # SSE format: "data: message\n\n"

# SSE endpoint for streaming responses
@app.get("/stream")
async def stream():
    """
    Endpoint that returns a streaming response.
    The frontend can connect to this endpoint to receive real-time updates.
    """
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream"  # Required for SSE
    )
