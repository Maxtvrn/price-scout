from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, index=True)
    brand = Column(String, index=True)
    model = Column(String, index=True)
    gtin = Column(String, index=True, unique=True)

    offers = relationship("Offer", back_populates="product")


class Offer(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    source = Column(String, index=True)
    seller = Column(String)
    price = Column(Float, nullable=False)
    delivery_price = Column(Float, default=0.0)
    delivery_days = Column(Integer, default=0)
    currency = Column(String, default="RUB")
    in_stock = Column(Boolean, default=True)
    url = Column(String)
    updated_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="offers")

    @property
    def total_price(self) -> float:
        return self.price + (self.delivery_price or 0.0)


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    source = Column(String, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
