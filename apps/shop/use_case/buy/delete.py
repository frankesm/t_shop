from config.database import session_scope
from shared.base_usecase import DestroyUseCase


class DeleteBuy(DestroyUseCase):

    def delete(self, pk):
        instance = self.get_or_fail(pk)
        with session_scope() as session:
            buy_manager = self.manager_class(session)
            buy_manager.delete(instance)
