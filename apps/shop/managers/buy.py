from sqlalchemy import func
from sqlalchemy.orm import selectinload

from apps.shop.managers.product import ProductManager
from apps.shop.models.buy import Buy
from apps.shop.models.product import Product
from shared.base_manager import BaseManager, icontains, gt, lt


class BuyManager(BaseManager):
    model = Buy
    ordering = (Buy.date.desc(), Buy.id.desc())
    filter_fields = {
        "code": icontains(Buy.code),
        "date_after": gt(Buy.date),
        "date_before": lt(Buy.date),
    }
    _product_count = func.count(Product.id)
    _product_cost = func.coalesce(func.sum(Product.buy_cost), 0)
    _total_cost = _product_cost + Buy.other_cost + Buy.transportation_cost

    ordering_fields = {
        "code": Buy.code,
        "date": Buy.date,
        "other_cost": Buy.other_cost,
        "transportation_cost": Buy.transportation_cost,
        "product_cost": _product_cost,
        "product_count": _product_count,
        "total_cost": _total_cost,
    }

    def get_list_query(self):
        return (
            self.session.query(Buy)
            .outerjoin(Product, Product.buy_id == Buy.id)
            .options(selectinload(Buy.products))
            .group_by(Buy.id)
        )

    def list(self, **filters):
        query = self.get_list_query()
        query = self.apply_filters(query, filters)
        query = self.apply_ordering(query, filters)
        return query.all()

    def create(self, data):
        products = data.pop("products")
        obj = self.model(**data)
        self.session.add(obj)
        self.session.flush()

        ProductManager(self.session).create(products, obj)
        return obj

    def update(self, obj: Buy, data):
        for field, value in data.items():
            setattr(obj, field, value)
        self.session.add(obj)
        self.session.flush()
        return obj

    def delete(self, obj: Buy):
        self.session.delete(obj)
        self.session.flush()
