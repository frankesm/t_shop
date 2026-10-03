from apps.shop.serializers.product import ProductSerializer
from shared.base_field import ListField
from shared.base_serializer import Serializer


class UpdateBuyProductsSerializer(Serializer):
    fields = {
        "products": ListField(child=ProductSerializer()),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current = {p.id: p for p in self.instance.products}

    def get_child_instance(self, field_name, data):
        pk = data.get("id")
        product = self.current.get(pk)
        return product

    def general_validate(self, data):
        codes = [row["code"] for row in data["products"]]

        if len(codes) != len(set(codes)):
            raise ValueError("Hay códigos de producto repetidos en la tabla.")

        return data
