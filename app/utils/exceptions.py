class NotFoundException(Exception):
    def __init__(self, detail: str = "Resource not found"):
        self.detail = detail

class ForbiddenException(Exception):
    def __init__(self, detail: str = "Insufficient permissions"):
        self.detail = detail

class UnauthorizedException(Exception):
    def __init__(self, detail: str = "Unauthorized"):
        self.detail = detail

class ConflictException(Exception):
    def __init__(self, detail: str = "Resource already exists"):
        self.detail = detail

class BadRequestException(Exception):
    def __init__(self, detail: str = "Bad request"):
        self.detail = detail