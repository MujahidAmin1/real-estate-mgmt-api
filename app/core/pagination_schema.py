
from typing import TypeVar, Generic, List

from pydantic import BaseModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
    
class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta
    