from fastapi import APIRouter, HTTPException, Request
import json
import threading
import asyncio
from backend.models import Vote
from backend.database import get_db_connection, write_vote_to_db
from backend.notifications import notify_display, send_udp_message
from backend.websocket import ConnectionManager
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="web-server/templates")
connection_manager = ConnectionManager()  # Create an instance to use

@router.post("/vote")
async def vote(vote_data: Vote):
    """
    A /vote végpont fogadja a beérkező szavazatokat.
    Először az adatbázisba írja a szavazatot, majd értesíti a kijelzőt REST és UDP üzenetekkel.
    """
    print(f"Received vote: {vote_data.name} - {vote_data.vote}")
    try:
        write_vote_to_db(vote_data)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to record vote")

    threading.Thread(target=notify_display, args=(vote_data,)).start()

    threading.Thread(
        target=send_udp_message, args=(f"New vote from {vote_data.name}",)
    ).start()

    # Broadcast to WebSocket clients
    vote_json = json.dumps({"name": vote_data.name, "vote": vote_data.vote})
    threading.Thread(target=asyncio.run, args=(ConnectionManager.broadcast(vote_json),)).start()

    return {"status": "success", "message": "Vote recorded."}

@router.post("/vote/{question_id}")
async def vote_for_question(question_id: int, vote_data: Vote):
    """Submit a vote for a specific question"""
    try:
        # Verify the question exists
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        question = cursor.fetchone()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
            
        if not question['active']:
            raise HTTPException(status_code=400, detail="This question is no longer active")
        
        # Record the vote
        write_vote_to_db(vote_data, question_id)
        
        # Notify about the vote
        threading.Thread(target=notify_display, args=(vote_data,)).start()
        threading.Thread(
            target=send_udp_message, args=(f"New vote from {vote_data.name} for question {question_id}",)
        ).start()
        
        # Broadcast to WebSocket clients
        vote_json = json.dumps({
            "question_id": question_id,
            "name": vote_data.name, 
            "vote": vote_data.vote
        })
        
        # Use asyncio.create_task instead of threading for async operations
        asyncio.create_task(connection_manager.broadcast(vote_json))
        
        return {"status": "success", "message": "Vote recorded."}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing vote: {e}")
        raise HTTPException(status_code=500, detail="Failed to process vote")
    finally:
        if "connection" in locals():
            cursor.close()
            connection.close()
