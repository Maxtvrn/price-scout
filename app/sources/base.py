from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class RawOffer:
    """Сырое предложение от источника до нормализации."""
    source: str
    seller: str
    title: str
    brand: str
    model: str
    gtin: str
    price: float
    delivery_price: float = 0.0
    delivery_days: int = 0
    currency: str = "RUB"
    in_stock: bool = True
    url: str = ""


class BaseSource(ABC):
    """Базовый интерфейс источника цен."""

    name: str = "base"

    @abstractmethod
    def fetch_offers(self) -> list[RawOffer]:
        """Вернуть список предложений от источника."""
        raise NotImplementedError
