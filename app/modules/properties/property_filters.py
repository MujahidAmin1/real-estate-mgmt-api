from pydantic import BaseModel

from app.modules.properties.property_enums import ListingType, PropertyStatus, PropertyType


class PropertyFilters(BaseModel):
    property_type: PropertyType | None = None
    min_price: float | None = None
    max_price: float | None = None
    listing_type: ListingType | None = None
    property_status: PropertyStatus | None = None
