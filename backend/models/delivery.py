from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    delivery_person = Column(String(100))
    delivery_address = Column(String(255), nullable=False)
    status = Column(String(30), default="pending")
    estimated_delivery = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())