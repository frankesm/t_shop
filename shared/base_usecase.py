from config.database import session_scope


class ListUseCase:
    def list(self, **filtros):
        with session_scope() as session:
            return self.manager_class(session).list(**filtros)


class RetrieveUseCase:
    def retrieve(self, pk):
        with session_scope() as session:
            return self.get_or_fail(self.manager_class(session), pk)


class CreateUseCase:
    def create(self, datos):
        validated_data = self.serializer_class(datos).validate()
        with session_scope() as session:
            return self.manager_class(session).create(**validated_data)


class UpdateUseCase:
    def update(self, pk, datos):
        validated_data = self.serializer_class(datos, parcial=True).validate()
        with session_scope() as session:
            manager = self.manager_class(session)
            obj = self.get_or_fail(manager, pk)
            return manager.update(obj, **validated_data)


class DestroyUseCase:
    def destroy(self, pk):
        with session_scope() as session:
            manager = self.manager_class(session)
            obj = self.get_or_fail(manager, pk)
            manager.delete(obj)
