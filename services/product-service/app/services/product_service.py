from sqlalchemy.orm import Session
from app.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate,ProductUpdate
from fastapi import HTTPException


class ProductService:

    @staticmethod
    def create_product(
        db: Session,
        product: ProductCreate
    ):
        return ProductRepository.create(db, product)
    
    @staticmethod
    def get_all_products(db: Session):
        return ProductRepository.get_all(db)
    
    @staticmethod
    def get_product_by_id(
        db: Session,
        product_id: int
    ):
        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return product
    
    @staticmethod
    def update_product(
        db: Session,
        product_id: int,
        updated_product: ProductUpdate
    ):

        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return ProductRepository.update(
            db,
            product,
            updated_product
        )
    @staticmethod
    def delete_product(
        db: Session,
        product_id: int
    ):

        product = ProductRepository.get_by_id(
            db,
            product_id
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        ProductRepository.delete(
            db,
            product
        )

    @staticmethod
    def get_product_for_order(
        db: Session,
        product_id: int
    ):
        product = ProductRepository.get_product_for_order(
            db,
            product_id
        )

        if product is None:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return product