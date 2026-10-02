from apps.shop.managers.buy import BuyManager
from apps.shop.serializers.buy import BuySerializer
from apps.shop.ui.buy.buy_view import BuyView

from apps.shop.use_case.buy.create import CreateBuy
from apps.shop.use_case.buy.delete import DeleteBuy
from apps.shop.use_case.buy.list import ListBuy
from apps.shop.use_case.buy.update import UpdateBuy
from apps.shop.use_case.buy.validate import ValidateBuy

from shared.base_controller import GenericController


class BuyController(
    ListBuy, CreateBuy, ValidateBuy, UpdateBuy, DeleteBuy, GenericController
):
    title = "Compras"
    manager_class = BuyManager
    serializer_class = BuySerializer
    ui_class = BuyView
