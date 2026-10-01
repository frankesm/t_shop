from typing import Callable


# --- helpers para declarar filtros de forma corta ---
def icontains(column):
    return lambda value: column.ilike(f"%{value}%")


def eq(column):
    return lambda value: column == value


def gt(column):
    return lambda value: column > value


def lt(column):
    return lambda value: column < value


def gte(column):
    return lambda value: column >= value


def lte(column):
    return lambda value: column <= value


class BaseManager:
    model = None
    ordering = ()
    filter_fields: dict[str, Callable] = {}
    ordering_fields: dict = {}

    def __init__(self, session):
        self.session = session

    # def list(self, **filters):
    #     query = self.get_list_query()
    #     query = self.apply_filters(query, filters)
    #     query = self.apply_ordering(query, filters)
    #     return query.all()
    #
    # def retrieve(self, pk):
    #     return self.session.get(self.model, pk)
    #
    # def update(self, onj, **fields):
    #     for key, value in fields.items():
    #         setattr(onj, key, value)
    #     self.session.flush()
    #     return onj
    #
    # def delete(self, obj):
    #     self.session.delete(obj)
    #
    # def create(self, data):
    #     obj = self.model(**data)
    #     self.session.add(obj)
    #     self.session.flush()
    #     return obj

    def get(self, **kwargs):
        return self.session.query(self.model).filter_by(**kwargs).first()

    def filter(self, **kwargs):
        return self.session.query(self.model).filter_by(**kwargs)

    def all(self):
        return self.session.query(self.model).all()

    def get_list_query(self):
        return self.session.query(self.model)

    def get_default_ordering(self):
        if self.ordering:
            return self.ordering
        return (self.model.id.desc(),)

    def apply_filters(self, query, filters):
        for name, build_clause in self.filter_fields.items():
            value = filters.get(name)

            if value is None or value == "":
                continue

            query = query.filter(build_clause(value))

        return query

    def apply_ordering(self, query, filters):
        column = self.ordering_fields.get(filters.get("ordering"))

        if column is None:
            return query.order_by(*self.get_default_ordering())

        if filters.get("ordering_desc"):
            return query.order_by(column.desc())

        return query.order_by(column.asc())
