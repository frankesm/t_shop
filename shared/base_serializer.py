import copy

from shared.exceptions import ValidacionError, GENERAL


class Serializer:

    fields = {}

    def __init__(self, data=None, parcial=False, instance=None):
        self.data = data or {}
        self.parcial = parcial
        self.instance = instance
        self.errors = {}
        self.validated_data = {}
        self.changed_fields = set()
        self._instance_resolver = None
        self.fields = copy.deepcopy(self.fields)

    def get_child_instance(self, field_name, data):
        return self.instance

    def _pass_instance_to_child(self, field_name, field):
        resolver = lambda data, name=field_name: self.get_child_instance(name, data)

        if isinstance(field, Serializer):
            field._instance_resolver = resolver
        elif hasattr(field, "instance_resolver"):
            field.instance_resolver = resolver

    def has_changed(self, field_name, value):
        if self.instance is None or not hasattr(self.instance, field_name):
            return True
        return getattr(self.instance, field_name) != value

    # -----------------------------------------------------
    # Limpieza y validación
    # -----------------------------------------------------

    def _clean_field(self, field_name, field, data):
        self._pass_instance_to_child(field_name, field)

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

        # Si un padre me asignó un resolver, le pregunto cuál es mi instancia
        if self._instance_resolver is not None:
            try:
                self.instance = self._instance_resolver(self.data)
            except Exception as e:
                self.errors[GENERAL] = [e.args[0] if e.args else str(e)]
                return False

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
