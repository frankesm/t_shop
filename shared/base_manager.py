class BaseManager:
    model = None
    ordering = ()

    def __init__(self, session):
        self.session = session

    def retrieve(self, pk):
        return self.session.get(self.model, pk)

    def update(self, onj, **fields):
        for key, value in fields.items():
            setattr(onj, key, value)
        self.session.flush()
        return onj

    def delete(self, obj):
        self.session.delete(obj)

    def get(self, **kwargs):
        return self.session.query(self.model).filter_by(**kwargs).first()

    def filter(self, **kwargs):
        return self.session.query(self.model).filter_by(**kwargs)

    def all(self):
        return self.session.query(self.model).all()
