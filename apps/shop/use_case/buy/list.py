from decimal import Decimal, ROUND_DOWN

from config.database import session_scope
from shared.base_usecase import ListUseCase


class ListBuy(ListUseCase):
    def list(self, **filters):
        with session_scope() as session:
            buys = self.manager_class(session).list()

            return [
                {
                    "id": b.id,
                    "date": b.date,
                    "code": b.code,
                    "product_count": len(b.products),
                    "product_cost": sum(product.buy_cost for product in b.products),
                    "other_cost": b.other_cost,
                    "transportation_cost": b.transportation_cost,
                    "total_cost": (
                        sum(product.buy_cost for product in b.products)
                        + b.other_cost
                        + b.transportation_cost
                    ),
                    "products": [
                        {
                            "code": p.code,
                            "name": p.name,
                            "unit": p.unit,
                            "amount": p.amount,
                            "buy_cost": p.buy_cost,
                            "unit_cost": (
                                Decimal(p.buy_cost) / Decimal(p.amount)
                            ).quantize(
                                Decimal("0.01"),
                                rounding=ROUND_DOWN,
                            ),
                        }
                        for p in b.products
                    ],
                }
                for b in buys
            ]
