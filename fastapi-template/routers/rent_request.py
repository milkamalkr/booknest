from fastapi import APIRouter, HTTPException, Depends
from db import get_connection
import routers.auth as auth
import routers.me as me
from math import ceil
from fastapi import Query

router = APIRouter()

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
    # Update latest rental_history for this book and renter to 'rented' and set rent_start
    cur.execute(
        """
        SELECT id FROM rental_history
        WHERE book_id = %s AND renter_id = %s AND status = 'pending'
        ORDER BY id DESC LIMIT 1
        """,
        (book_id, renter_id)
    )
    history_row = cur.fetchone()
    if history_row:
        cur.execute(
            "UPDATE rental_history SET status = 'rented', rent_start = NOW() WHERE id = %s",
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

@router.get("/rent-requests/my-outgoing")
def my_outgoing_rent_requests(
    status: str = Query(None, description="Filter by request status (pending, accepted, declined)"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: dict = Depends(me.get_current_user)
):
    conn = get_connection()
    cur = conn.cursor()
    params = [user["id"]]
    status_filter = ""
    if status:
        status_filter = "AND rr.status = %s"
        params.append(status)
    query = f'''
        SELECT rr.id as request_id, rr.book_id, b.title as book_title, b.owner_id as book_owner_id, b.image_url,
               rr.status, rr.request_date, rh.rent_start, rh.rent_end
        FROM rent_requests rr
        JOIN books b ON rr.book_id = b.id
        LEFT JOIN rental_history rh ON rh.book_id = rr.book_id AND rh.renter_id = rr.renter_id
        WHERE rr.renter_id = %s {status_filter}
        ORDER BY rr.request_date DESC
        LIMIT %s OFFSET %s
    '''
    params.extend([limit, offset])
    cur.execute(query, params)
    rows = cur.fetchall()
    results = []
    from datetime import datetime as dt
    for row in rows:
        rent_start = row["rent_start"]
        rent_end = row["rent_end"] or dt.utcnow()
        days = (rent_end - rent_start).days if rent_start else 0
        if rent_start and (rent_end - rent_start).seconds > 0:
            days += 1
        weeks = ceil(days / 7) if days > 0 else 1
        results.append({
            "request_id": row["request_id"],
            "book_id": row["book_id"],
            "book_title": row["book_title"],
            "book_owner_id": row["book_owner_id"],
            "image_url": row["image_url"],
            "request_date": row["request_date"],
            "weeks": weeks,
            "rental_history_status": row["status"],
            "rental_history_rent_end": row["rent_end"]
        })
    cur.close()
    conn.close()
    return results
