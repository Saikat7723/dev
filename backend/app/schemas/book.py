from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class CategoryResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class AuthorResponse(BaseModel):
    id: int
    name: str
    bio: Optional[str] = None

    class Config:
        from_attributes = True

class BookBase(BaseModel):
    isbn: str
    title: str
    author_id: Optional[int] = None
    category_id: Optional[int] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    edition: Optional[str] = None
    publication_year: Optional[int] = None
    total_copies: int = 1
    shelf_location: Optional[str] = None
    status: str = "Available"

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    isbn: Optional[str] = None
    title: Optional[str] = None
    author_id: Optional[int] = None
    category_id: Optional[int] = None
    publisher: Optional[str] = None
    description: Optional[str] = None
    edition: Optional[str] = None
    publication_year: Optional[int] = None
    total_copies: Optional[int] = None
    shelf_location: Optional[str] = None
    status: Optional[str] = None

class BookResponse(BookBase):
    id: int
    available_copies: int
    created_at: datetime
    updated_at: datetime
    author: Optional[AuthorResponse] = None
    category: Optional[CategoryResponse] = None

    class Config:
        from_attributes = True

class BookIssueCreate(BaseModel):
    student_id: int
    book_id: int
    issue_date: Optional[date] = None
    due_date: date
    notes: Optional[str] = None

class BookReturnRequest(BaseModel):
    return_date: Optional[date] = None
    fine_amount: Optional[float] = 0.0
    notes: Optional[str] = None

class BookIssueResponse(BaseModel):
    id: int
    student_id: int
    book_id: int
    issue_date: date
    due_date: date
    return_date: Optional[date] = None
    fine_amount: float
    status: str
    notes: Optional[str] = None
    created_at: datetime
    book: Optional[BookResponse] = None
    student_name: Optional[str] = None
    student_code: Optional[str] = None

    class Config:
        from_attributes = True
