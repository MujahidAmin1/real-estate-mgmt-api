class AdminError(Exception):
    pass


class CannotBanSelf(AdminError):
    def __init__(self, message: str = "You cannot ban yourself"):
        self.message = message
        super().__init__(self.message)
