from apps.shop.managers.product import ProductManager
from config.database import session_scope
from shared.base_field import CharField, IntegerField, PositiveDecimal
from shared.base_serializer import Serializer


class ProductSerializer(Serializer):

    fields = {
        "code": CharField(max_length=255),
        "name": CharField(max_length=255),
        "unit": CharField(max_length=255, required=False, default="Unidades"),
        "amount": IntegerField(min_value=1),
        "buy_cost": PositiveDecimal(),
    }

    def validate_code(self, data):
        with session_scope() as session:
            obj = ProductManager(session).get(code=data)
            if obj:
                raise ValueError("Ya existe un producto con ese código")
        return data
