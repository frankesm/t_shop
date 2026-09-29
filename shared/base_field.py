import math


class Field:
    def __init__(self, requerido=True, default=None):
        self.requerido = requerido
        self.default = default

    @staticmethod
    def is_empty(valor):
        return valor is None or (isinstance(valor, str) and not valor.strip())

    def clean(self, value):
        if self.is_empty(value):
            if self.requerido:
                raise Exception("Este campo es obligatorio.")
            return self.default
        return self.to_internal_value(value)

    def to_internal_value(self, value):
        return value


class CharField(Field):
    def __init__(self, max_length=None, **kwargs):
        super().__init__(**kwargs)
        self.max_length = max_length

    def to_internal_value(self, value):
        value = str(value).strip()
        if self.max_length and len(value) > self.max_length:
            raise Exception(f"Máximo {self.max_length} caracteres.")
        return value


class FloatField(Field):
    def __init__(self, min_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value

    def to_internal_value(self, value):
        if isinstance(value, str):
            value = value.strip().replace(",", ".")  # acepta "12,50"
        try:
            numero = float(value)
        except (TypeError, ValueError):
            raise Exception("Debe ser un número.")
        if not math.isfinite(numero):
            raise Exception("Debe ser un número.")
        if self.min_value is not None and numero < self.min_value:
            raise Exception(f"Debe ser mayor o igual a {self.min_value}.")
        return numero


class IntegerField(Field):
    def __init__(self, min_value=None, **kwargs):
        super().__init__(**kwargs)
        self.min_value = min_value

    def to_internal_value(self, value):
        try:
            numero = float(value)
        except (TypeError, ValueError):
            raise Exception("Debe ser un número entero.")
        if not numero.is_integer():  # rechaza 3.5, nan, inf
            raise Exception("Debe ser un número entero.")
        numero = int(numero)
        if self.min_value is not None and numero < self.min_value:
            raise Exception(f"Debe ser mayor o igual a {self.min_value}.")
        return numero
