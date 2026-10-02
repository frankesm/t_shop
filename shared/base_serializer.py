from shared.exceptions import ValidacionError, GENERAL


class Serializer:

    fields = {}

    def __init__(self, data=None, parcial=False, instance=None):
        self.data = data or {}
        self.parcial = parcial
        self.errors = {}
        self.validated_data = {}
        self.instance = instance
        self.changed_fields = set()

    def has_changed(self, field_name, value):
        if self.instance is None or not hasattr(self.instance, field_name):
            return True
        return getattr(self.instance, field_name) != value

    def _clean_field(self, field_name, field, data):
        value = field.clean(data.get(field_name))

        if not self.has_changed(field_name, value):
            return value  # mismo valor que ya tenía: se salta validate_<campo>

        self.changed_fields.add(field_name)

        validador = getattr(self, f"validate_{field_name}", None)
        if validador:
            value = validador(value)

        return value

    def is_valid(self):
        self.errors, self.validated_data = {}, {}
        self.changed_fields = set()

        for field_name, field_value in self.fields.items():
            if self.parcial and field_name not in self.data:
                continue
            try:
                self.validated_data[field_name] = self._clean_field(
                    field_name, field_value, self.data
                )
            except Exception as e:
                error = e.args[0] if e.args else str(e)

                if isinstance(error, (dict, list)):
                    self.errors[field_name] = error
                else:
                    self.errors.setdefault(field_name, []).append(error)

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

    def to_internal_value(self, data):
        validated_data = {}

        for field_name, field_value in self.fields.items():
            if self.parcial and field_name not in data:
                continue
            validated_data[field_name] = self._clean_field(
                field_name, field_value, data
            )

        return validated_data
