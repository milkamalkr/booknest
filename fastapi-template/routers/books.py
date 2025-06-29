from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import List, Optional, Any
from db import get_connection
from models.books_model  import BooksCreateRequest, BookCreate
import routers.auth as auth
import routers.me as me
from jose import jwt, JWTError
from .subscription import get_current_admin
from uuid import uuid4
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class BookOut(BaseModel):
    id: str
    title: str
    author: str
    published_year: int
    owner_id: str
    owner_name: str
    rent_per_week: int
    status: str
    current_renter_id: Optional[str] = None
    current_renter_name: Optional[str] = None
    created_at: datetime

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
            print("1111111111")
            cur.execute(
                """
                INSERT INTO books (id, title, author, owner_id, description, image_url, tags, published_year, created_at, current_renter_id, rent_per_week, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    book_id,
                    book.title,
                    book.author,
                    book.owner_id,
                    book.description,
                    book.image_url,
                    book.tags,
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

@router.get("/books", response_model=dict)
def list_books(
    title: Optional[str] = Query(None),
    author: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort_by: str = Query("title", pattern="^(title|created_at)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    user: dict = Depends(me.get_current_user)
):
    conn = get_connection()
    cur = conn.cursor()
    filters = []
    params = []
    if title:
        filters.append("b.title ILIKE %s")
        params.append(f"%{title}%")
    if author:
        filters.append("b.author ILIKE %s")
        params.append(f"%{author}%")
    if status:
        filters.append("b.status = %s")
        params.append(status)
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    # Count query
    count_query = f"SELECT COUNT(*) FROM books b {where_clause}"
    cur.execute(count_query, params)
    count_row = cur.fetchone()
    total = count_row["count"] if count_row and "count" in count_row else 0
    # Main query
    query = f"""
        SELECT b.*, o.name as owner_name, r.name as current_renter_name
        FROM books b
        LEFT JOIN users o ON b.owner_id = o.id
        LEFT JOIN users r ON b.current_renter_id = r.id
        {where_clause}
        ORDER BY b.{sort_by} {sort_order}
        LIMIT %s OFFSET %s
    """
    print("222222")
    cur.execute(query, params + [limit, offset])
    books = cur.fetchall()
    cur.close()
    conn.close()
    return {"total": total, "books": books}
