
from fastapi import APIRouter, HTTPException, Depends
from db import get_connection
import routers.auth as auth
import routers.me as me

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
