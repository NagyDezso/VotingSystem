from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from backend.database import get_db_connection
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="web-server/templates")


@router.get("/results")
async def get_results():
    """
    Szavazatok lekérdezése az adatbázisból.
    """
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Get raw vote data
        cursor.execute("SELECT name, vote FROM votes")
        votes = [dict(row) for row in cursor.fetchall()]

        # Get vote counts by option
        cursor.execute(
            """
            SELECT vote, COUNT(*) as count 
            FROM votes 
            GROUP BY vote 
            ORDER BY count DESC
        """
        )
        summary = [dict(row) for row in cursor.fetchall()]

        return {"votes": votes, "summary": summary}

    except Exception as e:
        print("Error retrieving results:", e)
        raise HTTPException(status_code=500, detail="Failed to retrieve results")
    finally:
        if "connection" in locals():
            cursor.close()
            connection.close()


@router.get("/results/{question_id}", response_class=HTMLResponse)
async def get_results_page(request: Request, question_id: int):
    """Show results page for a specific question"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Get question details
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        question = cursor.fetchone()

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        return templates.TemplateResponse(
            "results.html", {"request": request, "question": dict(question)}
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving question: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve question")
    finally:
        if "connection" in locals():
            cursor.close()
            connection.close()


@router.get("/api/results/{question_id}")
async def get_question_results_api(question_id: int):
    """Get results for a specific voting question"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Verify the question exists
        cursor.execute("SELECT title FROM questions WHERE id = ?", (question_id,))
        question = cursor.fetchone()

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        # Get raw vote data
        cursor.execute(
            "SELECT name, vote FROM votes WHERE question_id = ?", (question_id,)
        )
        votes = [dict(row) for row in cursor.fetchall()]

        # Get vote counts by option
        cursor.execute(
            """
            SELECT vote, COUNT(*) as count 
            FROM votes 
            WHERE question_id = ?
            GROUP BY vote 
            ORDER BY count DESC
        """,
            (question_id,),
        )
        summary = [dict(row) for row in cursor.fetchall()]

        return {"question": question["title"], "votes": votes, "summary": summary}
    except Exception as e:
        print(f"Error retrieving results: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve results")
    finally:
        if "connection" in locals():
            cursor.close()
            connection.close()
