import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    amount: int = Field(..., gt=0)
    category: str
    date: datetime.date
    note: Optional[str] = None

    @field_validator("category", mode="before")
    @classmethod
    def validate_and_strip_category(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Category must be a string")
        stripped = v.strip()
        if not stripped:
            raise ValueError("Category cannot be empty")
        return stripped.lower()

    @field_validator("note", mode="before")
    @classmethod
    def strip_note(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Note must be a string")
        return v.strip() if v.strip() else None


class ExpenseUpdate(BaseModel):
    amount: Optional[int] = Field(None, gt=0)
    category: Optional[str] = None
    date: Optional[datetime.date] = None
    note: Optional[str] = None

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, v: Any) -> Optional[int]:
        if v is None:
            raise ValueError("Amount cannot be null")
        return v

    @field_validator("category", mode="before")
    @classmethod
    def validate_and_strip_category(cls, v: Any) -> str:
        if v is None:
            raise ValueError("Category cannot be null")
        if not isinstance(v, str):
            raise ValueError("Category must be a string")
        stripped = v.strip()
        if not stripped:
            raise ValueError("Category cannot be empty")
        return stripped.lower()

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, v: Any) -> datetime.date:
        if v is None:
            raise ValueError("Date cannot be null")
        return v

    @field_validator("note", mode="before")
    @classmethod
    def strip_note(cls, v: Any) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise ValueError("Note must be a string")
        return v.strip() if v.strip() else None
