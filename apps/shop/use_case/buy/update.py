from config.database import session_scope
from shared.base_usecase import UpdateUseCase


class UpdateBuy(UpdateUseCase):

    def update(self, pk, data):
        instance = self.get_or_fail(pk)
        buy_serializer = self.serializer_class["update"](
            data, parcial=True, instance=instance
        )
        buy_serializer.validate()

        with session_scope() as session:
            buy_manager = self.manager_class(session)
            buy_manager.update(instance, buy_serializer.validated_data)
            return instance
