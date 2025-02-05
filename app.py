from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import get_db
from models import Product
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # どこからのアクセスも許可（本番では制限する）
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/product/{code}")
async def get_product(code: str, db: AsyncSession = Depends(get_db)):
    try:
        # CODEが整数型の場合、intに変換して検索
        result = await db.execute(select(Product).filter(Product.CODE == int(code)))
        product = result.scalars().first()

        if product:
            return {"name": product.NAME, "price": product.PRICE}
        else:
            raise HTTPException(status_code=404, detail="Product not found")

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid product code format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/debug/products")
async def debug_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product))
    products = result.scalars().all()
    return {"products": [ {"CODE": p.CODE, "NAME": p.NAME, "PRICE": p.PRICE} for p in products ]}
