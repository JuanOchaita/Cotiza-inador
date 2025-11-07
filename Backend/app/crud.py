from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.sql import Select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import auth, models, schemas


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    stmt = select(models.User).where(models.User.email == email)
    return db.scalars(stmt).first()


def create_user(db: Session, payload: schemas.UserCreate) -> models.User:
    if get_user_by_email(db, payload.email):
        raise ValueError("El correo ya está registrado.")

    user = models.User(name=payload.name, email=payload.email)
    db.add(user)
    db.flush()

    credential = models.UserCredential(user_id=user.user_id, password_hash=auth.hash_password(payload.password))
    db.add(credential)
    db.flush()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user or not user.credential:
        return None
    if not auth.verify_password(password, user.credential.password_hash):
        return None
    return user


def _collection_summary_stmt(user_id: int) -> Select:
    price_value = func.coalesce(
        func.sum(func.coalesce(models.Price.price_usd, 0) * func.coalesce(models.CardInCollection.quantity, 0)),
        0,
    ).label("total_value_usd")

    cards_count = func.coalesce(func.sum(models.CardInCollection.quantity), 0).label("cards_count")

    stmt = (
        select(
            models.Collection.id,
            models.Collection.name,
            models.Collection.description,
            models.Collection.created_at,
            price_value,
            cards_count,
        )
        .outerjoin(models.CardInCollection, models.CardInCollection.collection_id == models.Collection.id)
        .outerjoin(
            models.Price,
            and_(
                models.Price.card_id == models.CardInCollection.card_id,
                models.Price.condition_id == models.CardInCollection.condition_id,
            ),
        )
        .where(models.Collection.owner_id == user_id)
        .group_by(models.Collection.id)
        .order_by(models.Collection.created_at.desc())
    )
    return stmt


def list_collections(db: Session, user_id: int) -> list[schemas.CollectionSummary]:
    rows = db.execute(_collection_summary_stmt(user_id)).all()
    summaries: list[schemas.CollectionSummary] = []
    for row in rows:
        total_value = float(row.total_value_usd or 0)
        summaries.append(
            schemas.CollectionSummary(
                id=row.id,
                name=row.name,
                description=row.description,
                created_at=row.created_at,
                cards_count=int(row.cards_count or 0),
                total_value_usd=total_value,
            )
        )
    return summaries


def create_collection(
    db: Session,
    *,
    owner_id: int,
    name: str,
    description: Optional[str] = None,
) -> models.Collection:
    collection = models.Collection(owner_id=owner_id, name=name.strip(), description=description)
    db.add(collection)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise ValueError("Ya existe una colección con ese nombre.") from exc
    db.refresh(collection)
    return collection


def get_collection(db: Session, user_id: int, collection_id: int) -> Optional[models.Collection]:
    stmt = select(models.Collection).where(
        models.Collection.owner_id == user_id,
        models.Collection.id == collection_id,
    )
    return db.scalars(stmt).first()


def delete_collection(db: Session, user_id: int, collection_id: int) -> bool:
    collection = get_collection(db, user_id, collection_id)
    if not collection:
        return False
    db.delete(collection)
    return True


def get_collection_detail(db: Session, user_id: int, collection_id: int) -> Optional[schemas.CollectionDetail]:
    summary_stmt = _collection_summary_stmt(user_id).where(models.Collection.id == collection_id)
    summary_row = db.execute(summary_stmt).first()
    if not summary_row:
        return None

    cards_stmt = (
        select(
            models.CardInCollection.card_collection_id,
            models.CardInCollection.quantity,
            models.Card.name,
            models.Card.set_number,
            models.SetName.description.label("set_name"),
            models.CardCondition.description.label("condition"),
            models.Language.description.label("language"),
            models.Edition.description.label("edition"),
            models.Price.price_usd,
            models.Image.url.label("image_url"),
        )
        .join(models.Card, models.Card.card_id == models.CardInCollection.card_id)
        .join(models.SetName, models.SetName.set_name_id == models.Card.set_name_id)
        .join(models.CardCondition, models.CardCondition.condition_id == models.CardInCollection.condition_id)
        .join(models.Language, models.Language.language_id == models.Card.language_id)
        .join(models.Image, models.Image.image_url_id == models.Card.image_id)
        .outerjoin(models.Edition, models.Edition.edition_id == models.Card.edition_id)
        .outerjoin(
            models.Price,
            and_(
                models.Price.card_id == models.Card.card_id,
                models.Price.condition_id == models.CardInCollection.condition_id,
            ),
        )
        .where(models.CardInCollection.collection_id == collection_id)
        .order_by(models.CardInCollection.card_collection_id)
    )
    card_rows = db.execute(cards_stmt).all()

    cards: list[schemas.CardOut] = []
    for item in card_rows:
        value_usd = float(item.price_usd or Decimal("0"))
        cards.append(
            schemas.CardOut(
                card_collection_id=item.card_collection_id,
                name=item.name,
                set_number=item.set_number,
                set_name=item.set_name,
                condition=item.condition,
                language=item.language,
                version=item.edition,
                value_usd=value_usd,
                quantity=item.quantity,
                image_url=item.image_url,
            )
        )

    return schemas.CollectionDetail(
        id=summary_row.id,
        name=summary_row.name,
        description=summary_row.description,
        created_at=summary_row.created_at,
        cards_count=int(summary_row.cards_count or 0),
        total_value_usd=float(summary_row.total_value_usd or 0),
        cards=cards,
    )


def _get_or_create_language(db: Session, description: str) -> models.Language:
    stmt = select(models.Language).where(func.lower(models.Language.description) == description.lower())
    language = db.scalars(stmt).first()
    if language:
        return language
    language = models.Language(description=description)
    db.add(language)
    db.flush()
    return language


def _get_or_create_set_name(db: Session, description: str) -> models.SetName:
    stmt = select(models.SetName).where(func.lower(models.SetName.description) == description.lower())
    record = db.scalars(stmt).first()
    if record:
        return record
    record = models.SetName(description=description)
    db.add(record)
    db.flush()
    return record


def _get_or_create_condition(db: Session, description: str) -> models.CardCondition:
    stmt = select(models.CardCondition).where(func.lower(models.CardCondition.description) == description.lower())
    record = db.scalars(stmt).first()
    if record:
        return record
    record = models.CardCondition(description=description)
    db.add(record)
    db.flush()
    return record


def _get_or_create_edition(db: Session, description: Optional[str]) -> Optional[models.Edition]:
    if not description:
        return None
    stmt = select(models.Edition).where(func.lower(models.Edition.description) == description.lower())
    record = db.scalars(stmt).first()
    if record:
        return record
    record = models.Edition(description=description)
    db.add(record)
    db.flush()
    return record


def _get_or_create_image(db: Session, url: str) -> models.Image:
    stmt = select(models.Image).where(models.Image.url == url)
    record = db.scalars(stmt).first()
    if record:
        return record
    record = models.Image(url=url)
    db.add(record)
    db.flush()
    return record


def add_card_to_collection(
    db: Session,
    *,
    collection: models.Collection,
    payload: schemas.CardCreate,
) -> schemas.CardOut:
    condition = _get_or_create_condition(db, payload.condition)
    language = _get_or_create_language(db, payload.language)
    set_name_desc = payload.set_name or "Unknown Set"
    set_name = _get_or_create_set_name(db, set_name_desc)
    edition = _get_or_create_edition(db, payload.version)
    image_url = payload.image_url or "/placeholder.svg"
    image = _get_or_create_image(db, image_url)

    card_stmt = select(models.Card).where(
        models.Card.name == payload.name,
        models.Card.language_id == language.language_id,
        models.Card.set_name_id == set_name.set_name_id,
        models.Card.set_number == payload.set_number,
        models.Card.image_id == image.image_url_id,
        models.Card.edition_id == (edition.edition_id if edition else None),
    )
    card = db.scalars(card_stmt).first()
    if not card:
        card = models.Card(
            name=payload.name,
            language_id=language.language_id,
            set_name_id=set_name.set_name_id,
            set_number=payload.set_number,
            image_id=image.image_url_id,
            edition_id=edition.edition_id if edition else None,
        )
        db.add(card)
        db.flush()

    if payload.value_usd is None:
        value_usd = Decimal("0")
    else:
        value_usd = Decimal(str(payload.value_usd))

    price = models.Price(card_id=card.card_id, condition_id=condition.condition_id, price_usd=value_usd, date=datetime.utcnow())
    db.merge(price)

    quantity = payload.quantity or 1
    if quantity < 1:
        raise ValueError("La cantidad debe ser al menos 1.")

    card_entry = models.CardInCollection(
        collection_id=collection.id,
        card_id=card.card_id,
        condition_id=condition.condition_id,
        quantity=quantity,
    )
    db.add(card_entry)
    db.flush()

    return schemas.CardOut(
        card_collection_id=card_entry.card_collection_id,
        name=payload.name,
        set_number=payload.set_number,
        set_name=set_name.description,
        condition=condition.description,
        language=language.description,
        version=edition.description if edition else None,
        value_usd=float(value_usd),
        quantity=quantity,
        image_url=image_url,
    )


def delete_card_from_collection(db: Session, *, user_id: int, collection_id: int, card_collection_id: int) -> bool:
    stmt = (
        select(models.CardInCollection)
        .join(models.Collection, models.Collection.id == models.CardInCollection.collection_id)
        .where(
            models.Collection.owner_id == user_id,
            models.Collection.id == collection_id,
            models.CardInCollection.card_collection_id == card_collection_id,
        )
    )
    card_entry = db.scalars(stmt).first()
    if not card_entry:
        return False
    db.delete(card_entry)
    return True
