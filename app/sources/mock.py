import random

from app.sources.base import BaseSource, RawOffer


class MockSource(BaseSource):
    """Демо-источник с захардкоженными товарами и разбросом цен.
    Нужен, чтобы приложение работало без реальных парсеров."""

    def __init__(self, name: str, price_multiplier: float = 1.0, seed: int = 0):
        self.name = name
        self.price_multiplier = price_multiplier
        self.rng = random.Random(seed)

    def fetch_offers(self) -> list[RawOffer]:
        catalog = [
            ("Apple iPhone 15 128GB",        "Apple", "iPhone 15",   "194253397291", 79990),
            ("Apple iPhone 15 Pro 256GB",    "Apple", "iPhone 15 Pro", "194253398482", 129990),
            ("Samsung Galaxy S24 256GB",     "Samsung", "Galaxy S24", "8806095304742", 89990),
            ("Samsung Galaxy A55 128GB",     "Samsung", "Galaxy A55", "8806095470607", 34990),
            ("Xiaomi 14 256GB",              "Xiaomi", "Xiaomi 14",   "6941812754122", 69990),
            ("Xiaomi Redmi Note 13 Pro 256GB","Xiaomi", "Redmi Note 13 Pro", "6941812747919", 27990),
            ("Google Pixel 8 128GB",         "Google", "Pixel 8",     "0840244700477", 64990),
            ("OnePlus 12 256GB",             "OnePlus", "OnePlus 12", "6921815627803", 74990),
            ("Huawei P60 Pro 256GB",         "Huawei", "P60 Pro",     "6942103109053", 79990),
            ("Sony Xperia 1 V 256GB",        "Sony", "Xperia 1 V",    "4548736139740", 99990),
        ]

        offers = []
        for title, brand, model, gtin, base_price in catalog:
            # у каждого источника свой сдвиг цены и шум
            noise = self.rng.uniform(0.96, 1.04)
            price = round(base_price * self.price_multiplier * noise, -1)

            delivery_price = self.rng.choice([0, 0, 290, 390, 490])
            delivery_days = self.rng.choice([1, 2, 3, 5, 7])

            offers.append(RawOffer
