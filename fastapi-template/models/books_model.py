from typing import List
from datetime import datetime
from pydantic import BaseModel, validator
from typing import List, Optional, Any

class BookCreate(BaseModel):
    title: str
    author: str
    owner_id: str
    rent_per_week: int
    value: int
    published_year: int
    status: str = "available"
    current_renter_id: str | None = None
    created_at: datetime | None = None
    description: str | None = None
    image_url: str | None = None
    tags: List[str] | None = None

class BooksCreateRequest(BaseModel):
    books: List[BookCreate]

class BookOut(BaseModel):
    id: str
    title: str
    author: str
    published_year: int
    owner_id: str
    owner_name: str
    rent_per_week: int
    value: int
    status: str
    current_renter_id: Optional[str] = None
    current_renter_name: Optional[str] = None
    created_at: datetime
    description: str = None
    image_url: Optional[str] = None
    tags: List[str] = []

class BookUpdate(BaseModel):
    status: Optional[str] = None
    current_renter_id: Optional[str] = None

    @validator("status")
    def validate_status(cls, v):
        allowed = ["available", "rented", "pending"]
        if v is not None and v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v