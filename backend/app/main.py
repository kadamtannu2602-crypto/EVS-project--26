from fastapi import FastAPI
from sqlalchemy import text
from app.database import engine, Base

# Import all models
from models.user import User
from models.product import Product
from models.order import Order
from models.delivery import Delivery
from models.tracking import OrderTracking

# Import authentication router
from routes.auth import router as auth_router
from routes.products import router as products_router
from routes.orders import router as orders_router
from routes.delivery import router as delivery_router
from routes.tracking import router as tracking_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FarmDirect API")

# Register authentication routes
app.include_router(auth_router)
app.include_router(products_router)
app.include_router(orders_router)
app.include_router(delivery_router)
app.include_router(tracking_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to FarmDirect API!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.get("/test-db")
def test_database():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "status": "success"
        }

    except Exception as e:
        return {
            "database": "disconnected",
            "error": str(e)
        }