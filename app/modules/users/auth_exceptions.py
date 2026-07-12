class UserError(Exception):
    pass


class EmailAlreadyRegistered(UserError):
    def __init__(self, message: str = "Email already registered"):
        self.message = message
        super().__init__(self.message)


class UserNotFound(UserError):
    def __init__(self, message: str = "User not found"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(UserError):
    def __init__(self, message: str = "Invalid email or password"):
        self.message = message
        super().__init__(self.message)


class WrongTokenType(UserError):
    def __init__(self, message: str = "Wrong token type"):
        self.message = message
        super().__init__(self.message)


class TokenReuseDetected(UserError):
    def __init__(self, message: str = "Token reuse detected"):
        self.message = message
        super().__init__(self.message)
