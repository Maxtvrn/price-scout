from sqlalchemy.orm import Session

from app import models


def snapshot_prices(db: Session) -> int:
    """Сохраняет текущие цены всех предложений в историю."""
    offers = db.query(models.Offer).all()
    for offer in offers:
        db.add(models.PriceHistory(
            product_id=offer.product_id,
            source=offer.source,
            price=offer.price,
        ))
    db.commit()
    return len(offers)


def get_price_history(db: Session, product_id: int) -> list[dict]:
    """Возвращает историю цен товара, отсортированную по времени."""
    rows = db.query(models.PriceHistory).filter(
        models.PriceHistory.product_id == product_id
    ).order_by(models.PriceHistory.timestamp.asc()).all()

    return [
        {"timestamp": r.timestamp.isoformat(), "source": r.source, "price": r.price}
        for r in rows
    ]
