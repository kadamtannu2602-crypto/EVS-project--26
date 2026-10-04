from pydantic import BaseModel, Field


class TrackingCreate(BaseModel):
    order_id: int
    status: str
    location: str | None = None
    description: str | None = None
    updated_by: str | None = None