from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.session import get_db
from app.models.book import Book, BookCategory, BookAuthor
from app.models.system import AuditLog
from app.schemas.book import BookCreate, BookUpdate, BookResponse, CategoryResponse, AuthorResponse
from app.core.security import get_current_user, Admin

router = APIRouter(prefix="/books", tags=["Books"])

@router.get("", response_model=List[BookResponse])
def list_books(
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    author_id: Optional[int] = Query(None),
    status_filter: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    query = db.query(Book)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                Book.title.ilike(term),
                Book.isbn.ilike(term),
                Book.publisher.ilike(term)
            )
        )
    if category_id:
        query = query.filter(Book.category_id == category_id)
    if author_id:
        query = query.filter(Book.author_id == author_id)
    if status_filter:
        query = query.filter(Book.status == status_filter)

    books = query.order_by(Book.created_at.desc()).offset(skip).limit(limit).all()
    return books

@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    existing = db.query(Book).filter(Book.isbn == book_in.isbn).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Book with ISBN '{book_in.isbn}' already exists."
        )

    book = Book(
        **book_in.model_dump(),
        available_copies=book_in.total_copies
    )
    db.add(book)
    db.commit()
    db.refresh(book)

    audit = AuditLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action="BOOK_CREATE",
        target_type="Book",
        target_id=str(book.id),
        details=f"Added book '{book.title}' (ISBN: {book.isbn})"
    )
    db.add(audit)
    db.commit()

    return book

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(BookCategory).all()

@router.get("/authors", response_model=List[AuthorResponse])
def list_authors(db: Session = Depends(get_db)):
    return db.query(BookAuthor).all()

@router.get("/{id}", response_model=BookResponse)
def get_book(id: int, db: Session = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{id}", response_model=BookResponse)
def update_book(
    id: int,
    book_in: BookUpdate,
    db: Session = Depends(get_db),
    current_user: Admin = Depends(get_current_user)
):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    data = book_in.model_dump(exclude_unset=True)
    
    # Handle total copies modification
    if "total_copies" in data:
        diff = data["total_copies"] - book.total_copies
        book.available_copies = max(0, book.available_copies + diff)

    for field, val in data.items():
        setattr(book, field, val)

    if book.available_copies <= 0:
        book.status = "Out of Stock"
    elif book.status == "Out of Stock" and book.available_copies > 0:
        book.status = "Available"

    db.add(book)
    db.commit()
    db.refresh(book)

    audit = AuditLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action="BOOK_UPDATE",
        target_type="Book",
        target_id=str(book.id),
        details=f"Updated book '{book.title}'"
    )
    db.add(audit)
    db.commit()

    return book

@router.delete("/{id}")
def delete_book(id: int, db: Session = Depends(get_db), current_user: Admin = Depends(get_current_user)):
    book = db.query(Book).filter(Book.id == id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book.status = "Discontinued"
    db.add(book)
    db.commit()

    audit = AuditLog(
        admin_id=current_user.id,
        admin_email=current_user.email,
        action="BOOK_DELETE",
        target_type="Book",
        target_id=str(book.id),
        details=f"Discontinued book '{book.title}'"
    )
    db.add(audit)
    db.commit()

    return {"success": True, "message": f"Book '{book.title}' deleted/discontinued successfully"}
