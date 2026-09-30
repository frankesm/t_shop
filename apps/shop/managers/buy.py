from sqlalchemy.orm import selectinload

from apps.shop.managers.product import ProductManager
from apps.shop.models.buy import Buy
from shared.base_manager import BaseManager


class BuyManager(BaseManager):
    model = Buy

    def list(self, **filters):
        return (
            self.session.query(Buy)
            .options(selectinload(Buy.products))
            .order_by(Buy.date.desc(), Buy.id.desc())
            .all()
        )

    def create(self, data):
        products = data.pop("products")
        obj = self.model(**data)
        self.session.add(obj)
        self.session.flush()

        ProductManager(self.session).create(products, obj)
        return obj
