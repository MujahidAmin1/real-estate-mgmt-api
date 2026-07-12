class PropertyError(Exception):
    pass


class PropertyNotFound(PropertyError):
    def __init__(self, message: str = "Property not found"):
        self.message = message
        super().__init__(self.message)


class InvalidImageError(PropertyError):
    pass


class CloudinaryOperationError(PropertyError):
    pass


class ImageUploadError(PropertyError):
    pass


class FavoriteAlreadyExists(PropertyError):
    def __init__(self, message: str = "Property is already favorited"):
        self.message = message
        super().__init__(self.message)


class FavoriteNotFound(PropertyError):
    def __init__(self, message: str = "Favorite not found"):
        self.message = message
        super().__init__(self.message)
