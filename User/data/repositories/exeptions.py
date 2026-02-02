class RepoError(Exception):
    pass


class UniqueViolationError(RepoError):
    def __init__(self, field: str, value: str | None = None):
        self.field = field
        self.value = value
        msg = f"Unique constraint violated: {field}"
        if value is not None:
            msg += f"={value}"
        super().__init__(msg)
