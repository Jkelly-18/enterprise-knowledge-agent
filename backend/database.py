"""
# database.py

## What this file does:
Sets up the SQLAlchemy database connection and defines all table models
for the Velo enterprise-knowledge-agent backend. This file is the single
source of truth for the database schema in the backend.

Tables: departments, employees, hr_requests (pto and expense only)
Projects and IT tickets have been intentionally removed — the portal
focuses on HR knowledge and personal HR requests.

Imported by: agent.py, main.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import config
from sqlalchemy import (
    create_engine, Column, Integer, String,
    Float, Date, Boolean, ForeignKey, Text, DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Engine & Session
engine = create_engine(
    config.DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=config.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Department(Base):
    __tablename__ = "departments"
    id            = Column(Integer, primary_key=True)
    name          = Column(String, unique=True, nullable=False)
    team_lead     = Column(String, nullable=False)
    headcount     = Column(Integer, default=0)
    budget_usd    = Column(Float, default=0)
    slack_channel = Column(String)
    employees     = relationship("Employee", back_populates="dept")

class Employee(Base):
    __tablename__ = "employees"
    id            = Column(Integer, primary_key=True)
    name          = Column(String, nullable=False)
    email         = Column(String, unique=True, nullable=False)
    role          = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"))
    salary_usd    = Column(Float)
    start_date    = Column(Date)
    is_manager    = Column(Boolean, default=False)
    reports_to    = Column(Integer, ForeignKey("employees.id"), nullable=True)
    persona       = Column(String, nullable=True)
    dept          = relationship("Department", back_populates="employees")
    hr_requests   = relationship("HRRequest", back_populates="employee")

class HRRequest(Base):
    __tablename__ = "hr_requests"
    id            = Column(Integer, primary_key=True)
    request_type  = Column(String)   # pto / expense
    description   = Column(Text)
    status        = Column(String)   # pending / approved / denied
    employee_id   = Column(Integer, ForeignKey("employees.id"))
    submitted_at  = Column(DateTime)
    resolved_at   = Column(DateTime, nullable=True)
    employee      = relationship("Employee", back_populates="hr_requests")

# Dependencies
def get_db():
    """FastAPI dependency — yields a database session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_engine():
    """Returns the SQLAlchemy engine for use by the LangChain SQL agent tool."""
    return engine

# Main
if __name__ == "__main__":
    print("Database connection verified")
