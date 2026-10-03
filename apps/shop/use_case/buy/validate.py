class ValidateBuy:
    def validate(self, data):
        return self.serializer_class["create"](data, parcial=True).validate()
