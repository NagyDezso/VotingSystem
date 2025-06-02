from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from backend.middleware import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="web-server/templates")

@router.get("/", response_class=HTMLResponse)
async def get_home_page(request: Request):
    """Serve the home page HTML"""
    current_user = get_current_user(request) 
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": current_user 
    })

@router.get("/create-question", response_class=HTMLResponse)
async def get_create_question_page(request: Request):
    """Serve the question creation page"""
    return templates.TemplateResponse("create_question.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request):
    """Show dashboard with all questions and results"""
    return templates.TemplateResponse("dashboard.html", {"request": request})