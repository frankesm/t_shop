from apps.shop.serializers.update_buy_product import UpdateBuyProductsSerializer
from config.database import session_scope


class UpdateRemoveBuyProducts:

    def update_products(self, pk, data):
        with session_scope() as session:
            buy_manager = self.manager_class(session)
            buy = self.get_or_fail(pk, buy_manager)
            if not data:
                buy_manager.delete(buy)
                return

            serializer = UpdateBuyProductsSerializer({"products": data}, instance=buy)
            serializer.validate()
            data = serializer.validated_data

            current = {p.id: p for p in buy.products}
            kept_ids = {row["id"] for row in data["products"]}

            removed = [p for pid, p in current.items() if pid not in kept_ids]
            changes = [
                (current[row["id"]], {k: v for k, v in row.items() if k != "id"})
                for row in data["products"]
            ]
            buy_manager.update_products(changes, removed)
            return
