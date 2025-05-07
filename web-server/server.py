from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
import uvicorn
import os

# Import modules
from backend.database import setup_database
from backend.websocket import ConnectionManager
from routes import vote_routes, question_routes, results_routes, page_routes

app = FastAPI()

# Setup static files
app.mount("/static", StaticFiles(directory="web-server/static"), name="static")

# Create websocket manager
manager = ConnectionManager()

# Include routers
app.include_router(vote_routes.router)
app.include_router(question_routes.router)
app.include_router(results_routes.router)
app.include_router(page_routes.router)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket végpont a kijelző automatikus frissítéséhez.
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and wait for messages
            data = await websocket.receive_text()
            print(f"Received message: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

if __name__ == "__main__":
    print("Starting Voting System server...")
    print(f"Database configured at: {os.getenv('DB_HOST', 'localhost')}")
    print(f"Display notifications will be sent to: {os.getenv('DISPLAY_URL', 'http://localhost:8000')}")
    
    # Initialize the database tables
    setup_database()
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
