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
                    "cost": b.cost,
                    "transportation_cost": b.transportation_cost,
                    "products": [
                        {
                            "code": p.code,
                            "name": p.name,
                            "unit": p.unit,
                            "amount": p.amount,
                            "buy_cost": p.buy_cost,
                        }
                        for p in b.products
                    ],
                }
                for b in buys
            ]
