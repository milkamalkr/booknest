from typing import List
from datetime import datetime
from pydantic import BaseModel


class BookCreate(BaseModel):
    title: str
    author: str
    owner_id: str
    rent_per_week: int
    published_year: int
    status: str = "available"
    current_renter_id: str | None = None
    created_at: datetime | None = None
    description: str | None = None
    image_url: str | None = None
    tags: List[str] | None = None

class BooksCreateRequest(BaseModel):
    books: List[BookCreate]
