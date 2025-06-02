import sqlite3
import secrets
import smtplib
from email.mime.text import MIMEText
from fastapi import APIRouter, Request, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend import models
from backend.auth import hash_password, verify_password, create_session, validate_session, delete_session
from backend.database import get_db_connection
from backend.database import get_user_by_id


router = APIRouter()
templates = Jinja2Templates(directory="web-server/templates")

@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register_user(request: Request, response: Response):
    form_data = await request.form()
    username = form_data.get("username")
    email = form_data.get("email")
    password = form_data.get("password")
    confirm_password = form_data.get("confirm_password")
    
    if not username or not email or not password or not confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "All fields are required"
        })
    
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": "Passwords do not match"
        })
    
    password_hash = hash_password(password)
    connection = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        user_id = cursor.lastrowid
        connection.commit()
        
        session = create_session(user_id)
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="session_token", value=session.session_token, httponly=True, max_age=60*60*24*7)
        return response
    except sqlite3.IntegrityError as e:
        # Duplikált felhasználónév vagy email
        error_msg = "Username or email already exists"
    except Exception as e:
        print(f"Registration error: {e}")
        error_msg = "An error occurred during registration"
    finally:
        if connection:
            cursor.close()
            connection.close()
    
    return templates.TemplateResponse("register.html", {
        "request": request,
        "error": error_msg
    })

@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login_user(request: Request, response: Response):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or not verify_password(user["password_hash"], password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Hibás felhasználónév vagy jelszó!"})

    session = create_session(user["id"])
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie(key="session_token", value=session.session_token, httponly=True, max_age=7*24*60*60)
    return response

@router.get("/logout")
async def logout_user(request: Request, response: Response):
    session_token = request.cookies.get("session_token")
    if session_token:
        delete_session(session_token)
    
    response = RedirectResponse(url="/")
    response.delete_cookie("session_token")
    return response

@router.get("/me")
def get_current_user(request: Request):
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        return None
    user = get_user_by_id(user_id)
    return user

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_page(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

@router.post("/forgot-password")
async def forgot_password(request: Request):
    form = await request.form()
    email = form.get("email")
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    if not user:
        cursor.close()
        connection.close()
        return templates.TemplateResponse("forgot_password.html", {"request": request, "error": "Nincs ilyen email!"})

    # Token generálás és adatbázisba mentés
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO password_resets (user_id, token, expires_at) VALUES (?, ?, ?)", (user["id"], token, expires_at))
    connection.commit()
    cursor.close()
    connection.close()

    # Email küldés
    reset_link = f"http://localhost:8000/reset-password?token={token}"
    msg = MIMEText(f"Kattints ide a jelszó visszaállításához: {reset_link}")
    msg["Subject"] = "Jelszó visszaállítás"
    msg["From"] = "noreply@votingsystem.local"
    msg["To"] = email

    # SMTP példa (állítsd be a saját szervered!)
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)

    return templates.TemplateResponse("forgot_password.html", {"request": request, "success": "Email elküldve!"})

    