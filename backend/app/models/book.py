from datetime import datetime, date
from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database.session import Base

class BookCategory(Base):
    __tablename__ = "book_categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(Text, nullable=True)

    books = relationship("Book", back_populates="category")

class BookAuthor(Base):
    __tablename__ = "book_authors"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), index=True, nullable=False)
    bio = Column(Text, nullable=True)

    books = relationship("Book", back_populates="author")

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    isbn = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(200), index=True, nullable=False)
    author_id = Column(Integer, ForeignKey("book_authors.id", ondelete="SET NULL"), nullable=True)
    category_id = Column(Integer, ForeignKey("book_categories.id", ondelete="SET NULL"), nullable=True)
    publisher = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    edition = Column(String(30), nullable=True)
    publication_year = Column(Integer, nullable=True)
    total_copies = Column(Integer, default=1, nullable=False)
    available_copies = Column(Integer, default=1, nullable=False)
    shelf_location = Column(String(50), nullable=True)
    status = Column(String(20), default="Available", nullable=False) # Available / Out of Stock / Discontinued
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    author = relationship("BookAuthor", back_populates="books")
    category = relationship("BookCategory", back_populates="books")
    issues = relationship("BookIssue", back_populates="book", cascade="all, delete-orphan")

class BookIssue(Base):
    __tablename__ = "book_issues"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    issue_date = Column(Date, default=date.today, nullable=False, index=True)
    due_date = Column(Date, nullable=False, index=True)
    return_date = Column(Date, nullable=True, index=True)
    fine_amount = Column(Float, default=0.0, nullable=False)
    status = Column(String(20), default="ISSUED", nullable=False, index=True) # ISSUED / RETURNED / OVERDUE
    notes = Column(Text, nullable=True)
    issued_by_admin_id = Column(Integer, ForeignKey("admins.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    student = relationship("Student", back_populates="book_issues")
    book = relationship("Book", back_populates="issues")
