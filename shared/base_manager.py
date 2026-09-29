from sqlalchemy import func


class BaseManager:
    model = None
    ordering = ()

    def __init__(self, session):
        self.session = session

    def list(self, **filtros):
        query = self.session.query(self.model).filter_by(**filtros)

        if self.ordering:
            ordering = [func.lower(field) for field in self.ordering]
            query = query.order_by(*ordering)

        return query.all()

    def retrieve(self, pk):
        return self.session.get(self.model, pk)

    def create(self, **fields):
        obj = self.model(**fields)
        self.session.add(obj)
        self.session.flush()
        return obj

    def update(self, onj, **fields):
        for key, value in fields.items():
            setattr(onj, key, value)
        self.session.flush()
        return onj

    def delete(self, obj):
        self.session.delete(obj)
