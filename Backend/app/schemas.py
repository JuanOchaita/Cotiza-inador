from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserOut(UserBase):
    user_id: int
    created_at: Optional[datetime] = None


class AuthResponse(Token):
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class CollectionBase(BaseModel):
    name: str
    description: Optional[str] = None


class CollectionCreate(CollectionBase):
    exchange_rate: Optional[float] = None


class CollectionSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    cards_count: int
    total_value_usd: float


class CollectionOut(CollectionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class CardBase(BaseModel):
    name: str
    set_number: Optional[str] = None
    set_name: Optional[str] = None
    condition: str
    language: str
    version: Optional[str] = None
    value_usd: float = 0.0
    quantity: int = 1
    image_url: Optional[str] = Field(default=None, alias="imageUrl")


class CardCreate(CardBase):
    pass


class CardOut(CardBase):
    card_collection_id: int

    class Config:
        allow_population_by_field_name = True


class CollectionDetail(BaseModel):
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    cards_count: int
    total_value_usd: float
    cards: list[CardOut]
