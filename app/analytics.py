from sqlalchemy.orm import Session

from app import models
from app.history import get_price_history


def get_best_offers(db: Session) -> list[dict]:
    """Для каждого товара — лучшие предложения по цене с учётом доставки."""
    products = db.query(models.Product).all()
    result = []

    for product in products:
        offers = [o for o in product.offers if o.in_stock]
        if not offers:
            continue

        sorted_offers = sorted(offers, key=lambda o: o.total_price)
        best = sorted_offers[0]

        result.append({
            "product_id": product.id,
            "title": product.title,
            "brand": product.brand,
            "model": product.model,
            "best_price": best.price,
            "best_delivery": best.delivery_price,
            "best_total": round(best.total_price, 2),
            "best_source": best.source,
            "best_seller": best.seller,
            "best_url": best.url,
            "offers_count": len(offers),
            "offers": [
                {
                    "source": o.source,
                    "seller": o.seller,
                    "price": o.price,
                    "delivery_price": o.delivery_price,
                    "delivery_days": o.delivery_days,
                    "total": round(o.total_price, 2),
                    "in_stock": o.in_stock,
                    "url": o.url,
                }
                for o in sorted_offers
            ],
        })

    result.sort(key=lambda x: x["title"])
    return result


def get_price_stats(db: Session) -> list[dict]:
    """Статистика: минимальная, максимальная цена и разброс по каждому товару."""
    products = db.query(models.Product).all()
    stats = []

    for product in products:
        offers = [o for o in product.offers if o.in_stock]
        if not offers:
            continue

        totals = [o.total_price for o in offers]
        min_price = min(totals)
        max_price = max(totals)
        spread = max_price - min_price
        spread_pct = round((spread / min_price) * 100, 1) if min_price else 0.0

        stats.append({
            "product_id": product.id,
            "title": product.title,
            "min_total": round(min_price, 2),
            "max_total": round(max_price, 2),
            "spread": round(spread, 2),
            "spread_percent": spread_pct,
            "offers_count": len(offers),
        })

    stats.sort(key=lambda x: x["spread"], reverse=True)
    return stats


def get_product_detail(db: Session, product_id: int) -> dict | None:
    """Детальная информация по одному товару + история цен."""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        return None

    offers = sorted(product.offers, key=lambda o: o.total_price)
    return {
        "product_id": product.id,
        "title": product.title,
        "brand": product.brand,
        "model": product.model,
        "gtin": product.gtin,
        "offers": [
            {
                "source": o.source,
                "seller": o.seller,
                "price": o.price,
                "delivery_price": o.delivery_price,
                "delivery_days": o.delivery_days,
                "total": round(o.total_price, 2),
                "in_stock": o.in_stock,
                "url": o.url,
            }
            for o in offers
        ],
        "history": get_price_history(db, product_id),
    }


def get_category_summary(db: Session) -> list[dict]:
    """Сводка по категориям: сколько товаров и средний разброс цен."""
    products = db.query(models.Product).all()
    categories: dict[str, dict] = {}

    for product in products:
        cat = product.category or "Без категории"
        offers = [o for o in product.offers if o.in_stock]
