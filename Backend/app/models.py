from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "user"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    credential: Mapped["UserCredential"] = relationship(
        "UserCredential", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    collections: Mapped[list["Collection"]] = relationship(
        "Collection", back_populates="owner", cascade="all, delete-orphan"
    )


class UserCredential(Base):
    __tablename__ = "user_credentials"

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped[User] = relationship("User", back_populates="credential")


class Collection(Base):
    __tablename__ = "collections"
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_user_collection_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped[User] = relationship("User", back_populates="collections")
    cards: Mapped[list["CardInCollection"]] = relationship(
        "CardInCollection", back_populates="collection", cascade="all, delete-orphan"
    )


class Language(Base):
    __tablename__ = "language"

    language_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    cards: Mapped[list["Card"]] = relationship("Card", back_populates="language")


class Edition(Base):
    __tablename__ = "edition"

    edition_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    cards: Mapped[list["Card"]] = relationship("Card", back_populates="edition")


class SetName(Base):
    __tablename__ = "set_name"

    set_name_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    cards: Mapped[list["Card"]] = relationship("Card", back_populates="set_name")


class Image(Base):
    __tablename__ = "image"

    image_url_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(Text, unique=True, nullable=False)

    cards: Mapped[list["Card"]] = relationship("Card", back_populates="image")


class Card(Base):
    __tablename__ = "card"

    __table_args__ = (
        UniqueConstraint(
            "name",
            "language_id",
            "set_name_id",
            "set_number",
            "image_id",
            "edition_id",
            name="card_unique",
        ),
    )

    card_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    language_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("language.language_id"), nullable=False
    )
    set_name_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("set_name.set_name_id"), nullable=False
    )
    set_number: Mapped[Optional[str]] = mapped_column(String(120))
    image_id: Mapped[int] = mapped_column(Integer, ForeignKey("image.image_url_id"), nullable=False)
    edition_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("edition.edition_id"))

    language: Mapped[Language] = relationship("Language", back_populates="cards")
    set_name: Mapped[SetName] = relationship("SetName", back_populates="cards")
    image: Mapped[Image] = relationship("Image", back_populates="cards")
    edition: Mapped[Optional[Edition]] = relationship("Edition", back_populates="cards")
    prices: Mapped[list["Price"]] = relationship(
        "Price", back_populates="card", cascade="all, delete-orphan"
    )
    instances: Mapped[list["CardInCollection"]] = relationship(
        "CardInCollection", back_populates="card"
    )


class CardCondition(Base):
    __tablename__ = "card_condition"

    condition_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)

    prices: Mapped[list["Price"]] = relationship("Price", back_populates="condition")
    cards: Mapped[list["CardInCollection"]] = relationship(
        "CardInCollection", back_populates="condition"
    )


class Price(Base):
    __tablename__ = "price"

    card_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("card.card_id"), primary_key=True
    )
    condition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("card_condition.condition_id"), primary_key=True
    )
    price_usd: Mapped[Numeric] = mapped_column(Numeric(10, 2), nullable=False)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    card: Mapped[Card] = relationship("Card", back_populates="prices")
    condition: Mapped[CardCondition] = relationship("CardCondition", back_populates="prices")


class CardInCollection(Base):
    __tablename__ = "card_in_collection"

    card_collection_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    collection_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False
    )
    card_id: Mapped[int] = mapped_column(Integer, ForeignKey("card.card_id"), nullable=False)
    condition_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("card_condition.condition_id"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    collection: Mapped[Collection] = relationship("Collection", back_populates="cards")
    card: Mapped[Card] = relationship("Card", back_populates="instances")
    condition: Mapped[CardCondition] = relationship("CardCondition", back_populates="cards")

