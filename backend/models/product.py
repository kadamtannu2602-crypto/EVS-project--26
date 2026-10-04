from sqlalchemy import Column, Integer, String, ForeignKey, Text, Numeric
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    category = Column(String(50))
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)