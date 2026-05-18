from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("ProductServiceDeployed")
# DATABASE_URL = os.getenv("ProductServiceLocal")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL_Local = DATABASE_URL
engine = create_engine(DATABASE_URL_Local)


# Get all products
@app.get("/products")
def get_products():

    try:
        with engine.connect() as conn:

            result = conn.execute(text("SELECT * FROM Products"))

            products = [dict(row._mapping) for row in result]

        return products

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching products"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )


# Get product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):

    try:
        with engine.connect() as conn:

            result = conn.execute(
                text("SELECT * FROM Products WHERE product_id = :id"),
                {"id": product_id}
            )

            product = result.fetchone()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return dict(product._mapping)

    except HTTPException as e:
        raise e

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching product"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )


# Create product
@app.post("/products")
def create_product(product: dict):

    try:
        with engine.connect() as conn:

            conn.execute(text("""
                INSERT INTO Products 
                (product_id, title, description, price, stock, category, image_url)
                VALUES 
                (:product_id, :title, :description, :price, :stock, :category, :image_url)
            """), product)

            conn.commit()

        return {
            "message": "Product created"
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Database error while creating product"
        )

    except KeyError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required field: {str(e)}"
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unexpected server error"
        )