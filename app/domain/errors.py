class AppError(Exception):
    def __init__(self, status: int, error: str, message: str, details: list[dict] | None = None):
        super().__init__(message)
        self.status = status
        self.error = error
        self.message = message
        self.details = details or []
        