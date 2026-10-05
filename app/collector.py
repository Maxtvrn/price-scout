from sqlalchemy.orm import Session

from app import models
from app.sources.base import BaseSource, RawOffer
from app.sources.mock import get_sources


def _find_or_create_product(db: Session, offer: RawOffer) -> models.Product:
    product = None
    if offer.gtin:
        product = db.query(models.Product).filter(models.Product.gtin == offer.gtin).first()

    if product is None and offer.model:
        product = db.query(models.Product).filter(
            models.Product.model == offer.model,
            models.Product.brand == offer.brand,
        ).first()

    if product is None:
        product = models.Product(
            title=offer.title,
            category="Смартфоны",
            brand=offer.brand,
            model=offer.model,
            gtin=offer.gtin or None,
        )
        db.add(product)
        db.flush()

    return product


def save_offers(db: Session, offers: list[RawOffer]) -> int:
    """Сохраняет/обновляет предложения в БД. Возвращает число обработанных."""
    saved = 0
    for raw in offers:
        product = _find_or_create_product(db, raw)

        existing = db.query(models.Offer).filter(
            models.Offer.product_id == product.id,
            models.Offer.source == raw.source,
            models.Offer.seller == raw.seller,
        ).first()

        if existing:
            existing.price = raw.price
            existing.delivery_price = raw.delivery_price
            existing.delivery_days = raw.delivery_days
            existing.in_stock = raw.in_stock
            existing.url = raw.url
        else:
            db.add(models.Offer(
                product_id=product.id,
                source=raw.source,
                seller=raw.seller,
                price=raw.price,
                delivery_price=raw.delivery_price,
                delivery_days=raw.delivery_days,
                currency=raw.currency,
                in_stock=raw.in_stock,
                url=raw.url,
            ))
        saved += 1

    db.commit()
    return saved


def collect_all(db: Session, sources: list[BaseSource] | None = None) -> dict:
    """Собирает данные со всех источников."""
    sources = sources or get_sources()
    report = {}
    for source in sources:
        try:
            offers = source.fetch_offers()
            count = save_offers(db, offers)
            report[source.name] = {"ok": True, "saved": count}
        except Exception as exc:  # noqa: BLE001
            report[source.name] = {"ok": False, "error": str(exc)}
    return report
