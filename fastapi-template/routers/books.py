from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import List, Optional, Any
from db import get_connection
from models.books_model  import BooksCreateRequest, BookCreate, BookOut, BookUpdate
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
    for book in books_req.books:
        print(book)
        book_id = str(uuid4())
        created_at = datetime.utcnow()
        # You may want to extend BookCreate model to accept these fields from input
        current_renter_id = None
        
        
        try:
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
    cur.execute(query, params + [limit, offset])
    books = cur.fetchall()
    cur.close()
    conn.close()
    return {"total": total, "books": books}

@router.get("/books/{id}", response_model=BookOut)
def get_book(
    id: str,
    user: dict = Depends(me.get_current_user)
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        '''
        SELECT b.*, o.name as owner_name, r.name as current_renter_name
        FROM books b
        LEFT JOIN users o ON b.owner_id = o.id
        LEFT JOIN users r ON b.current_renter_id = r.id
        WHERE b.id = %s
        ''',
        (id,)
    )
    book = cur.fetchone()
    cur.close()
    conn.close()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.patch("/books/{id}", response_model=BookOut)
def update_book(
    id: str,
    update: BookUpdate,
    user: dict = Depends(me.get_current_user)
):
    # Check admin or owner
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT owner_id FROM books WHERE id = %s", (id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    is_owner = row["owner_id"] == user["id"]
    if not (user.get("is_admin") or is_owner):
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Admin or owner access required")
    if update.status is None and update.current_renter_id is None:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="No fields to update")
    # Validate current_renter_id if provided
    if update.current_renter_id is not None:
        cur.execute("SELECT id FROM users WHERE id = %s", (update.current_renter_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            raise HTTPException(status_code=400, detail="current_renter_id does not exist")
    # Build update query
    set_clauses = []
    params = []
    if update.status is not None:
        set_clauses.append("status = %s")
        params.append(update.status)
    if update.current_renter_id is not None:
        set_clauses.append("current_renter_id = %s")
        params.append(update.current_renter_id)
    params.append(id)
    set_clause = ", ".join(set_clauses)
    cur.execute(f"UPDATE books SET {set_clause} WHERE id = %s RETURNING *", params)
    book = cur.fetchone()
    if not book:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    # Get owner and renter names
    cur.execute(
        '''
        SELECT b.*, o.name as owner_name, r.name as current_renter_name
        FROM books b
        LEFT JOIN users o ON b.owner_id = o.id
        LEFT JOIN users r ON b.current_renter_id = r.id
        WHERE b.id = %s
        ''',
        (id,)
    )
    book = cur.fetchone()
    cur.close()
    conn.close()
    return book

@router.post("/books/{id}/request")
def request_rent(
    id: str,
    user: dict = Depends(me.get_current_user)
):
    conn = get_connection()
    cur = conn.cursor()
    # Validate book exists
    cur.execute("SELECT owner_id FROM books WHERE id = %s", (id,))
    book = cur.fetchone()
    if not book:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    # User is not the owner
    if book["owner_id"] == user["id"]:
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Owner cannot request to rent their own book")
    # User does not already have a rent request for this book (pending/accepted)
    cur.execute(
        """
        SELECT 1 FROM rent_requests WHERE book_id = %s AND renter_id = %s AND status IN ('pending', 'accepted')
        """,
        (id, user["id"])
    )
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="You already have a pending or accepted rent request for this book")
    # Insert into rent_requests
    cur.execute(
        """
        INSERT INTO rent_requests (book_id, renter_id, status, request_date)
        VALUES (%s, %s, 'pending', NOW())
        RETURNING id
        """,
        (id, user["id"])
    )
    rent_request_id = cur.fetchone()["id"]
    # Insert into rental_history
    cur.execute(
        """
        INSERT INTO rental_history (book_id, renter_id, status, rented_by_owner_id, rent_start)
        VALUES (%s, %s, 'pending', NULL, NOW())
        RETURNING id
        """,
        (id, user["id"])
    )
    rental_history_id = cur.fetchone()["id"]
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Rent request submitted", "rent_request_id": rent_request_id, "rental_history_id": rental_history_id}

@router.patch("/rent-requests/{id}/accept")
def accept_rent_request(
    id: str,
    user: dict = Depends(me.get_current_user)
):
    conn = get_connection()
    cur = conn.cursor()
    # Get rent request and book
    cur.execute("SELECT book_id, renter_id, status FROM rent_requests WHERE id = %s", (id,))
    req = cur.fetchone()
    if not req:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Rent request not found")
    if req["status"] != "pending":
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Request is not pending")
    book_id = req["book_id"]
    renter_id = req["renter_id"]
    # Check if user is book owner
    cur.execute("SELECT owner_id FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    if not book:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Book not found")
    if book["owner_id"] != user["id"]:
        cur.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Only the book owner can accept requests")
    # Accept the rent request
    cur.execute("UPDATE rent_requests SET status = 'accepted' WHERE id = %s", (id,))
    # Set book status and current_renter_id
    cur.execute("UPDATE books SET status = 'rented', current_renter_id = %s WHERE id = %s", (renter_id, book_id))
    # Update latest rental_history for this book and renter to 'rented'
    # Find the latest rental_history id
    cur.execute(
        """
        SELECT id FROM rental_history
        WHERE book_id = %s AND renter_id = %s AND status = 'pending'
        ORDER BY rent_start DESC LIMIT 1
        """,
        (book_id, renter_id)
    )
    history_row = cur.fetchone()
    if history_row:
        cur.execute(
            "UPDATE rental_history SET status = 'rented' WHERE id = %s",
            (history_row["id"],)
        )
    # Remove accepted user from waitlists for this book (delete other pending requests for this user/book)
    cur.execute(
        "DELETE FROM rent_requests WHERE book_id = %s AND renter_id = %s AND status = 'pending' AND id != %s",
        (book_id, renter_id, id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Rent request accepted and book rented"}
