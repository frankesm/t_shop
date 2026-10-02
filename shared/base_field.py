import math


class Field:
    def __init__(self, required=True, default=None):
        self.required = required
        self.default = default

    @staticmethod
    def is_empty(valor):
        return valor is None or (isinstance(valor, str) and not valor.strip())

    def clean(self, value):
        if self.is_empty(value):
            if self.required:
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


from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_DOWN


class DateField(Field):
    formats = ("%Y-%m-%d", "%d/%m/%Y")

    def to_internal_value(self, value):
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        for fmt in self.formats:
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except ValueError:
                continue
        raise Exception("Fecha inválida. Usa el formato dd/mm/aaaa.")


class DecimalField(Field):
    def __init__(self, min_value=None, decimal_places=2, **kwargs):
        super().__init__(**kwargs)
        self.min_value = None if min_value is None else Decimal(str(min_value))
        self.quantum = Decimal(1).scaleb(-decimal_places)

    def to_internal_value(self, value):
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
        try:
            number = Decimal(str(value))
        except (InvalidOperation, ValueError):
            raise Exception("Debe ser un número.")
        if not number.is_finite():
            raise Exception("Debe ser un número.")
        number = number.quantize(self.quantum, rounding=ROUND_DOWN)
        if self.min_value is not None and number < self.min_value:
            raise Exception(f"Debe ser mayor o igual a {self.min_value}.")
        return number


class PositiveDecimal(DecimalField):
    def to_internal_value(self, value):
        number = super().to_internal_value(value)

        if number < 0:
            raise Exception("Debe ser un número positivo.")

        return number


class ListField(Field):
    def __init__(self, child, min_items=1, **kwargs):
        super().__init__(**kwargs)
        self.child = child
        self.min_items = min_items

    def to_internal_value(self, value):
        name = getattr(self.child, "verbose_name", "Elemento")

        if not isinstance(value, (list, tuple)):
            raise Exception("Debe ser una lista.")
        if len(value) < self.min_items:
            raise Exception(f"Agrega al menos {self.min_items} {name.lower()}.")

        serializer_class = type(self.child)
        items, errors = [], []
        for raw in value:
            serializer = serializer_class(raw)
            if serializer.is_valid():
                items.append(serializer.validated_data)
                errors.append({})
            else:
                items.append(None)
                errors.append(dict(serializer.errors))
        if any(errors):
            raise Exception(errors)
        return items
