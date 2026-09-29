from config import settings

GENERAL = settings.GENERAL_ERROR


class ValidacionError(Exception):

    def __init__(self, errors):
        if isinstance(errors, str):
            errors = {GENERAL: [errors]}
        self.errors = errors
        super().__init__(self.message())

    def message(self):
        lines = []
        for field, msg in self.errors.items():
            for m in msg:
                lines.append(m if field == GENERAL else f"{field}: {m}")
        return "\n".join(lines)
