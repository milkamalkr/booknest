from fastapi import APIRouter, HTTPException, Depends, Header
from typing import List
from db import get_connection
from models.users import BooksCreateRequest, BookCreate
import routers.auth as auth
import routers.me as me
from jose import jwt, JWTError
from .subscription import get_current_admin
from uuid import uuid4
from datetime import datetime

router = APIRouter()



@router.post("/books")
def add_books(
    books_req: BooksCreateRequest,
    admin_user: dict = Depends(get_current_admin)
):
    conn = get_connection()
    cur = conn.cursor()
    inserted = []
    print("inside")
    for book in books_req.books:
        print(book)
        book_id = str(uuid4())
        created_at = datetime.utcnow()
        # You may want to extend BookCreate model to accept these fields from input
        current_renter_id = None
        
        
        try:
            cur.execute(
                """
                INSERT INTO books (id, title, author, owner_id, published_year, created_at, current_renter_id, rent_per_week, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    book_id,
                    book.title,
                    book.author,
                    book.owner_id,
                    book.published_year,
                    created_at,
                    current_renter_id,
                    book.rent_per_week,
                    book.status
                )
            )
            inserted.append({"id": book_id, "title": book.title})
        except Exception as e:
            print(f"Error inserting book: {e}")
            conn.rollback()
            continue
    conn.commit()
    cur.close()
    conn.close()
    if not inserted:
        raise HTTPException(status_code=400, detail="No books inserted")
    return {"inserted": inserted}
