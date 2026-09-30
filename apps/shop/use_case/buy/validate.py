class ValidateBuy:
    def validate(self, data):
        return self.serializer_class(data, parcial=True).validate()
