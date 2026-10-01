from sqlalchemy import func
from sqlalchemy.orm import selectinload

from apps.shop.managers.product import ProductManager
from apps.shop.models.buy import Buy
from apps.shop.models.product import Product
from shared.base_manager import BaseManager


class BuyManager(BaseManager):
    model = Buy

    def list(self, **filters):
        product_cost = func.coalesce(
            func.sum(Product.buy_cost),
            0,
        )

        product_count = func.count(Product.id)

        total_cost = product_cost + Buy.other_cost + Buy.transportation_cost

        query = (
            self.session.query(
                Buy,
                product_count.label("product_count"),
                product_cost.label("product_cost"),
                total_cost.label("total_cost"),
            )
            .outerjoin(Product, Product.buy_id == Buy.id)
            .options(selectinload(Buy.products))
            .group_by(Buy.id)
        )

        code = filters.get("code")

        if code:
            query = query.filter(Buy.code.ilike(f"%{code}%"))

        date_after = filters.get("date_after")

        if date_after:
            query = query.filter(Buy.date > date_after)

        date_before = filters.get("date_before")

        if date_before:
            query = query.filter(Buy.date < date_before)

        ordering = filters.get("ordering")

        ordering_fields = {
            "code": Buy.code,
            "date": Buy.date,
            "product_count": product_count,
            "product_cost": product_cost,
            "other_cost": Buy.other_cost,
            "transportation_cost": Buy.transportation_cost,
            "total_cost": total_cost,
        }

        if ordering in ordering_fields:
            order_column = ordering_fields[ordering]

            if filters.get("ordering_desc"):
                query = query.order_by(order_column.desc())
            else:
                query = query.order_by(order_column.asc())
        else:
            query = query.order_by(
                Buy.date.desc(),
                Buy.id.desc(),
            )

        return [buy for buy, _, _, _ in query.all()]

    def create(self, data):
        products = data.pop("products")
        obj = self.model(**data)
        self.session.add(obj)
        self.session.flush()

        ProductManager(self.session).create(products, obj)
        return obj
