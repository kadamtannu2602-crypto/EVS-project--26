from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.order import Order
from models.tracking import OrderTracking
from schemas.tracking import TrackingCreate

router = APIRouter(prefix="/tracking", tags=["Order Tracking"])


@router.post("/update")
def create_tracking_update(
    tracking_data: TrackingCreate,
    db: Session = Depends(get_db)
):
    # Check whether order exists
    order = db.query(Order).filter(
        Order.id == tracking_data.order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Create a new tracking record
    new_tracking = OrderTracking(
        order_id=tracking_data.order_id,
        status=tracking_data.status,
        location=tracking_data.location,
        description=tracking_data.description,
        updated_by=tracking_data.updated_by
    )

    # Save tracking update
    db.add(new_tracking)
    db.commit()
    db.refresh(new_tracking)

    return {
        "message": "Tracking update added successfully",
        "tracking_id": new_tracking.id,
        "order_id": new_tracking.order_id,
        "status": new_tracking.status,
        "location": new_tracking.location,
        "description": new_tracking.description,
        "updated_by": new_tracking.updated_by,
        "updated_at": new_tracking.updated_at
    }

@router.get("/{order_id}")
def get_order_tracking(
    order_id: int,
    db: Session = Depends(get_db)
):
    # Check whether order exists
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    # Get all tracking updates for this order
    tracking_history = db.query(OrderTracking).filter(
        OrderTracking.order_id == order_id
    ).order_by(
        OrderTracking.updated_at.asc()
    ).all()

    return {
        "order_id": order_id,
        "total_updates": len(tracking_history),
        "tracking_history": tracking_history
    }