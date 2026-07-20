from __future__ import annotations


class AppError(Exception):
    """Single application-level exception with an HTTP status code and message."""

    def __init__(self, status_code: int = 500, detail: str = "Internal server error"):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)
