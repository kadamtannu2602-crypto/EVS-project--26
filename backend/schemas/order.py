from pydantic import BaseModel, Field


class OrderCreate(BaseModel):
    customer_id: int
    product_id: int
    quantity: int = Field(gt=0)