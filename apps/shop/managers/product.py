from apps.shop.models.buy import Buy
from apps.shop.models.product import Product
from shared.base_manager import BaseManager


class ProductManager(BaseManager):
    model = Product

    def create_many(self, data: list[dict], obj: Buy):
        obj.products.extend(self.model(**item) for item in data)
        self.session.flush()

    def delete_many(self, products: list[Product]):
        for product in products:
            self.session.delete(product)
        self.session.flush()

    def update_many(self, changes: list[tuple[Product, dict]]):
        for product, data in changes:
            for field, value in data.items():
                setattr(product, field, value)
        self.session.flush()
