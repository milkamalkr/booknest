from fastapi import APIRouter, Depends, HTTPException, Header, Path
from jose import jwt, JWTError
from db import get_connection
import routers.auth as auth
from pydantic import BaseModel
import routers.me as me
from passlib.context import CryptContext
from models.users import UserRegister
from uuid import uuid4

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SubscriptionUpdate(BaseModel):
    subscription_type: str  # "basic" or "premium"
    max_limit: int

def get_current_admin(authorization: str = Header(...)):
    user = me.get_current_user(authorization)
    if not user or not user["is_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

@router.patch("/{id}/subscription")
def update_subscription(
    id: str = Path(..., description="User ID to update"),
    sub: SubscriptionUpdate = Depends(),
    admin_user: dict = Depends(get_current_admin)
):
    print("999999")
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute(
        "UPDATE users SET subscription_type = %s, max_limit = %s WHERE id = %s RETURNING id",
        (sub.subscription_type, sub.max_limit, id)
    )
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "Subscription updated", "user_id": id}



@router.post("/register")
def register(user: UserRegister, admin_user: dict = Depends(get_current_admin)):
    password_hash = pwd_context.hash(user.password)

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (id, name, email, phone, is_admin, subscription_type, max_limit, current_total, password_hash)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s)
        """, (
            str(uuid4()), user.name, user.email, user.phone, False,
            user.subscription_type, 500 if user.subscription_type == "basic" else 1000,
            password_hash
        ))

        conn.commit()
        return {"msg": "User registered successfully"}

    except Exception as e:
        raise HTTPException(status_code=400, detail="Email may already exist")

    finally:
        cur.close()
        conn.close()