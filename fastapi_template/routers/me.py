from fastapi import APIRouter, Depends, HTTPException, Header
from jose import jwt, JWTError
from db import get_connection
from models.users import UserRegister, UserLogin
import routers.auth as auth




router = APIRouter()

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id = payload.get("id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    # Fetch user from DB

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, email, phone, is_admin, subscription_type, max_limit, current_total FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

