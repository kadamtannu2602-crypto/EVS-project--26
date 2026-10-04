from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.delivery import Delivery
from models.order import Order
from schemas.delivery import DeliveryCreate, DeliveryStatusUpdate

router = APIRouter(prefix="/deliveries", tags=["Deliveries"])


@router.post("/create")
def create_delivery(
    delivery_data: DeliveryCreate,
    db: Session = Depends(get_db)
):
    # Check whether order exists
    order = db.query(Order).filter(
        Order.id == delivery_data.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Check whether delivery already exists
    existing_delivery = db.query(Delivery).filter(
        Delivery.order_id == delivery_data.order_id
    ).first()

    if existing_delivery:
        raise HTTPException(
            status_code=400,
            detail="Delivery already exists for this order"
        )

    # Create delivery
    new_delivery = Delivery(
        order_id=delivery_data.order_id,
        delivery_person=delivery_data.delivery_person,
        delivery_address=delivery_data.delivery_address,
        status="pending"
    )

    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)

    return {
        "message": "Delivery created successfully",
        "delivery_id": new_delivery.id,
        "order_id": new_delivery.order_id,
        "delivery_person": new_delivery.delivery_person,
        "delivery_address": new_delivery.delivery_address,
        "status": new_delivery.status
    }

@router.put("/{delivery_id}/status")
def update_delivery_status(
    delivery_id: int,
    status_data: DeliveryStatusUpdate,
    db: Session = Depends(get_db)
):
    # Find delivery
    delivery = db.query(Delivery).filter(
        Delivery.id == delivery_id
    ).first()

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    # Allowed statuses
    allowed_statuses = ["pending", "shipped", "delivered"]

    if status_data.status.lower() not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail="Invalid delivery status"
        )

    # Update status
    delivery.status = status_data.status.lower()

    db.commit()
    db.refresh(delivery)

    return {
        "message": "Delivery status updated successfully",
        "delivery_id": delivery.id,
        "status": delivery.status
    }

@router.get("/{delivery_id}")
def get_delivery(
    delivery_id: int,
    db: Session = Depends(get_db)
):
    # Find delivery by ID
    delivery = db.query(Delivery).filter(
        Delivery.id == delivery_id
    ).first()

    if not delivery:
        raise HTTPException(
            status_code=404,
            detail="Delivery not found"
        )

    return {
        "delivery_id": delivery.id,
        "order_id": delivery.order_id,
        "delivery_person": delivery.delivery_person,
        "delivery_address": delivery.delivery_address,
        "status": delivery.status,
        "estimated_delivery": delivery.estimated_delivery,
        "created_at": delivery.created_at
    }

@router.get("/")
def get_all_deliveries(db: Session = Depends(get_db)):

    deliveries = db.query(Delivery).all()

    return deliveries