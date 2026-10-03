from decimal import Decimal

from apps.shop.managers.buy import BuyManager
from apps.shop.serializers.product import ProductSerializer
from config.database import session_scope
from shared.base_field import DateField, PositiveDecimal, ListField, CharField
from shared.base_serializer import Serializer


class BuySerializer(Serializer):
    fields = {
        "date": DateField(),
        "other_cost": PositiveDecimal(required=False, default=Decimal("0.00")),
        "transportation_cost": PositiveDecimal(required=False, default=Decimal("0.00")),
        "code": CharField(),
        "products": ListField(child=ProductSerializer()),
    }

    def validate_code(self, data):
        with session_scope() as session:
            obj = BuyManager(session).get(code=data)
            if obj:
                raise ValueError("Ya existe un producto con ese código")
        return data


class BuyUpdateSerializer(Serializer):
    fields = {
        "date": DateField(),
        "other_cost": PositiveDecimal(required=False, default=Decimal("0.00")),
        "transportation_cost": PositiveDecimal(required=False, default=Decimal("0.00")),
        "code": CharField(),
    }

    def validate_code(self, data):
        with session_scope() as session:
            obj = BuyManager(session).get(code=data)
            if obj:
                raise ValueError("Ya existe un producto con ese código")
        return data
