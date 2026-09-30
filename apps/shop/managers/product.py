from apps.shop.models.buy import Buy
from apps.shop.models.product import Product
from shared.base_manager import BaseManager


class ProductManager(BaseManager):
    model = Product

    def create(self, data: list[dict], obj: Buy):
        obj.products.extend(self.model(**item) for item in data)
        self.session.flush()
