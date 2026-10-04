from pydantic import BaseModel


class DeliveryCreate(BaseModel):
    order_id: int
    delivery_person: str
    delivery_address: str


class DeliveryStatusUpdate(BaseModel):
    status: str