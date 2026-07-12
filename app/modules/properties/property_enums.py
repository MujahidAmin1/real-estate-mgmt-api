import enum

class PropertyType(str, enum.Enum):
    house = "house"
    apartment = "apartment"
    land = "land"
    commercial = "commercial"

class ListingType(str, enum.Enum):
    sale = "sale"
    rent = "rent"
    shortlet = "shortlet"

class PropertyStatus(str, enum.Enum):
    available = "available"
    sold = "sold"
    rented = "rented"
    inactive = "inactive"
