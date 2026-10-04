from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from models.product import Product
from models.user import User
from schemas.product import ProductCreate


router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/add")
def add_product(product_data: ProductCreate, db: Session = Depends(get_db)):

    # Check whether the farmer exists
    farmer = db.query(User).filter(
        User.id == product_data.farmer_id
    ).first()

    if not farmer or farmer.role != "farmer":
        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    # Create a new product
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        quantity=product_data.quantity,
        category=product_data.category,
        farmer_id=product_data.farmer_id
    )

    # Save product to database
    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return {
        "message": "Product added successfully",
        "product_id": new_product.id,
        "name": new_product.name,
        "price": new_product.price,
        "quantity": new_product.quantity,
        "category": new_product.category,
        "farmer_id": new_product.farmer_id
    }

@router.get("/")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return products

@router.get("/{product_id}")
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product

@router.put("/{product_id}")
def update_product(product_id: int, product_data: ProductCreate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = product_data.name
    product.description = product_data.description
    product.price = product_data.price
    product.quantity = product_data.quantity
    product.category = product_data.category

    db.commit()
    db.refresh(product)

    return {
        "message": "Product updated successfully",
        "product_id": product.id,
        "name": product.name,
        "price": product.price,
        "quantity": product.quantity,
        "category": product.category,
        "farmer_id": product.farmer_id
    }

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {
        "message": "Product deleted successfully",
        "product_id": product_id
    }