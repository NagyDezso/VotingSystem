from fastapi import Request, HTTPException
from backend.auth import validate_session
from fastapi import Request
from typing import Optional
from backend.database import get_user_by_id


async def auth_middleware(request: Request, call_next):
    # Skip authentication for public routes (de NEM a főoldalra!)
    public_routes = ["/register", "/login", "/logout", "/static"]
    if any(request.url.path.startswith(route) for route in public_routes):
        return await call_next(request)
    
    # Check session for protected routes ÉS a főoldal
    session_token = request.cookies.get("session_token")
    if session_token:
        user_id = validate_session(session_token)
        if user_id:
            request.state.user_id = user_id

    return await call_next(request)

def get_current_user(request: Request):
    user_id = getattr(request.state, "user_id", None)
    if user_id is None:
        return None
    return get_user_by_id(user_id)