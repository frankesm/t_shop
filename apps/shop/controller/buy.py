from apps.shop.managers.buy import BuyManager
from apps.shop.serializers.buy import BuySerializer, BuyUpdateSerializer
from apps.shop.serializers.update_buy_product import UpdateBuyProductsSerializer
from apps.shop.ui.buy.buy_view import BuyView
from apps.shop.use_case.buy.create import CreateBuy
from apps.shop.use_case.buy.delete import DeleteBuy
from apps.shop.use_case.buy.list import ListBuy
from apps.shop.use_case.buy.update import UpdateBuy
from apps.shop.use_case.buy.update_remove_buy_product import UpdateRemoveBuyProducts
from apps.shop.use_case.buy.validate import ValidateBuy
from shared.base_controller import GenericController


class BuyController(
    ListBuy,
    CreateBuy,
    ValidateBuy,
    UpdateBuy,
    DeleteBuy,
    UpdateRemoveBuyProducts,
    GenericController,
):
    title = "Compras"
    manager_class = BuyManager
    serializer_class = {
        "create": BuySerializer,
        "update": BuyUpdateSerializer,
        "update_products": UpdateBuyProductsSerializer,
    }
    ui_class = BuyView
