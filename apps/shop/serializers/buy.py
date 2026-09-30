from decimal import Decimal

from apps.shop.serializers.product import ProductSerializer
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

    # def general_validate(self, data):
    #     if data.get("products", None):
    #         total_cost = Decimal("0.00")
    #         for item in data["products"]:
    #             total_cost += item["buy_cost"]
    #
    #         if total_cost != data["cost"]:
    #             raise ValueError(
    #                 "El precio total de los productos debe ser igual al costo de la compra"
    #             )
    #
    #     return data
