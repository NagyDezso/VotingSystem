from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from typing import List
from backend.models import Question, QuestionResponse
from backend.database import get_db_connection
from routes.common import templates

router = APIRouter()


@router.get("/questions", response_model=List[QuestionResponse])
async def get_questions(active_only: bool = True):
    """Retrieve all voting questions"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if active_only:
            cursor.execute("SELECT * FROM questions WHERE active = 1 ORDER BY created_at DESC")
        else:
            cursor.execute("SELECT * FROM questions ORDER BY created_at DESC")

        questions = cursor.fetchall()

        # Get options for each question
        result = []
        for question in questions:
            cursor.execute(
                "SELECT option_text FROM options WHERE question_id = ?",
                (question['id'],)
            )
            options = [row['option_text'] for row in cursor.fetchall()]

            question_with_options = {
                "id": question['id'],
                "title": question['title'],
                "description": question['description'],
                "options": options,
                "active": bool(question['active'])  # Convert integer to boolean
            }
            result.append(question_with_options)

        return result
    except Exception as e:
        print(f"Error retrieving questions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve questions")
    finally:
        if "connection" in locals():
            cursor.close()
            connection.close()


@router.post("/questions")
async def create_question(question: Question):
    """Create a new voting question with options"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Insert question
        cursor.execute(
            "INSERT INTO questions (title, description) VALUES (?, ?)",
            (question.title, question.description)
        )
        question_id = cursor.lastrowid

        # Insert options
        for option in question.options:
            cursor.execute(
                "INSERT INTO options (question_id, option_text) VALUES (?, ?)",
                (question_id, option)
            )

        connection.commit()
        return {"id": question_id, "status": "success", "message": "Question created successfully"}
    except Exception as e:
        print(f"Error creating question: {e}")
        raise HTTPException(status_code=500, detail="Failed to create question")
    finally:
        if "connection" in locals():
            cursor.close()
            connection.close()


@router.get("/question/{question_id}", response_class=HTMLResponse)
async def get_question_page(request: Request, question_id: int):
    """Get voting page for a specific question"""
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Get question details
        cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
        question = cursor.fetchone()

        if not question:
            raise HTTPException(status_code=404, detail="Question not found")

        # Get options
        cursor.execute("SELECT option_text FROM options WHERE question_id = ?", (question_id,))
        options = [row['option_text'] for row in cursor.fetchall()]

        return templates.TemplateResponse(
            "vote.html",
            {
                "request": request,
                "question": dict(question),  # Convert Row to dict
                "options": options
            }
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
