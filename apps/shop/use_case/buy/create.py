from config.database import session_scope
from shared.base_usecase import CreateUseCase


class CreateBuy(CreateUseCase):

    def create(self, data):
        buy_serializer = self.serializer_class(data)
        buy_serializer.validate()

        with session_scope() as session:
            buy_manager = self.manager_class(session)
            buy = buy_manager.create(buy_serializer.validated_data)
            return buy
