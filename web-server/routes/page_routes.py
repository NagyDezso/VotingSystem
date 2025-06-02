from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from routes.common import templates

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):
    """Serve the home page HTML"""
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/create-question", response_class=HTMLResponse)
async def get_create_question_page(request: Request):
    """Serve the question creation page"""
    return templates.TemplateResponse("create_question.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Show dashboard with all questions and results"""
    return templates.TemplateResponse("dashboard.html", {"request": request})
