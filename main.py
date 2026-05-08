from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
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

#  Get all products
@app.get("/products")
def get_products():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM Products"))
        products = [dict(row._mapping) for row in result]
    return products


#  Get product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM Products WHERE product_id = :id"),
            {"id": product_id}
        )
        product = result.fetchone()
    return dict(product._mapping) if product else {"error": "Not found"}


#  Create product
@app.post("/products")
def create_product(product: dict):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO Products (product_id, title, description, price, stock, category, image_url)
            VALUES (:product_id, :title, :description, :price, :stock, :category, :image_url)
        """), product)
        conn.commit()
    return {"message": "Product created"}