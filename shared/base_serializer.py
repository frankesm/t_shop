from shared.exceptions import ValidacionError, GENERAL


class Serializer:

    fields = {}

    def __init__(self, data, parcial=False):
        self.data = data or {}
        self.parcial = parcial
        self.errors = {}
        self.validated_data = {}

    def is_valid(self):
        self.errors, self.validated_data = {}, {}

        for field_name, field_value in self.fields.items():
            if self.parcial and field_name not in self.data:
                continue
            try:
                value = field_value.clean(self.data.get(field_name))
                validador = getattr(self, f"validate_{field_name}", None)
                if validador:
                    value = validador(value)
                self.validated_data[field_name] = value
            except Exception as e:
                self.errors.setdefault(field_name, []).append(str(e))

        if not self.errors:
            try:
                self.validated_data = self.general_validate(self.validated_data)
            except Exception as e:
                self.errors[GENERAL] = [str(e)]

        return not self.errors

    def general_validate(self, data):
        return data

    def validate(self):
        if not self.is_valid():
            raise ValidacionError(self.errors)
        return self.validated_data
