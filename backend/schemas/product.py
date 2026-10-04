from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: float = Field(gt=0)
    quantity: int = Field(ge=0)
    category: str
    farmer_id: int