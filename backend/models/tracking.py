from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

from app.database import Base


class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False
    )

    status = Column(String, nullable=False)

    location = Column(String, nullable=True)

    description = Column(Text, nullable=True)

    updated_by = Column(String, nullable=True)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )