class ProfileError(Exception):
    pass


class ProfileNotFound(ProfileError):
    def __init__(self, message: str = "Profile not found"):
        self.message = message
        super().__init__(self.message)
