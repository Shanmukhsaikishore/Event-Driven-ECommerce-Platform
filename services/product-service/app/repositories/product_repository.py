from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate,ProductUpdate
from app.models.product import Product


class ProductRepository:

    @staticmethod
    def create(db: Session, product: ProductCreate) -> Product:
        new_product = Product(
            name=product.name,
            description=product.description,
            price=product.price
        )

        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return new_product


    @staticmethod
    def get_all(db: Session) -> list[Product]:
        return db.query(Product).all()
    
    @staticmethod
    def get_by_id(db: Session, product_id: int) -> Product | None:
        return (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )
    

    @staticmethod
    def update(
        db: Session,
        product: Product,
        updated_product: ProductUpdate
    ) -> Product:

        product.name = updated_product.name
        product.description = updated_product.description
        product.price = updated_product.price

        db.commit()
        db.refresh(product)

        return product
    

    @staticmethod
    def delete(
        db: Session,
        product: Product
    ) -> None:
        db.delete(product)
        db.commit()
    
    @staticmethod
    def get_product_for_order(db: Session, product_id: int) -> Product | None:
        return (
            db.query(Product)
            .filter(Product.id == product_id)
            .first()
        )