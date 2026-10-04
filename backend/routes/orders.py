from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.order import Order
from models.product import Product
from models.user import User
from schemas.order import OrderCreate

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/place")
def place_order(order_data: OrderCreate, db: Session = Depends(get_db)):

    # Check whether customer exists
    customer = db.query(User).filter(
        User.id == order_data.customer_id
    ).first()

    if not customer or customer.role != "customer":
        raise HTTPException(status_code=404, detail="Customer not found")

    # Check whether product exists
    product = db.query(Product).filter(
        Product.id == order_data.product_id
    ).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check product availability
    if product.quantity < order_data.quantity:
        raise HTTPException(
            status_code=400,
            detail="Insufficient product quantity"
        )

    # Calculate total price
    total_price = product.price * order_data.quantity

    # Create new order
    new_order = Order(
        customer_id=order_data.customer_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
        total_price=total_price,
        status="pending"
    )

    # Reduce product stock
    product.quantity -= order_data.quantity

    # Save changes
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return {
        "message": "Order placed successfully",
        "order_id": new_order.id,
        "customer_id": new_order.customer_id,
        "product_id": new_order.product_id,
        "quantity": new_order.quantity,
        "total_price": new_order.total_price,
        "status": new_order.status
    }