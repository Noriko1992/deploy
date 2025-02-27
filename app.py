from fastapi import FastAPI, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from connect import SessionLocal
from models import Product, Transaction, TransactionDetail
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 設定
origins = ["https://tech0-gen8-step4-pos-app-53.azurewebsites.net"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 商品カートアイテムモデル
class CartItem(BaseModel):
    code: str
    name: str
    price: int
    quantity: int = 1

# 購入リクエストモデル
class PurchaseRequest(BaseModel):
    emp_cd: str
    store_cd: Optional[str] = "30"
    pos_no: Optional[str] = "90"
    items: List[CartItem] = []

# DB セッションの取得
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 商品情報取得エンドポイント
@app.get("/product/{code}")
def get_product(code: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.code == code).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品が見つかりません")
    return {"product": {"code": product.code, "name": product.name, "price": product.price}}

@app.get("/")
def read_root():
    return {"message": "FastAPI is running!"}

@app.post("/purchase")
def handle_purchase(request: PurchaseRequest, db: Session = Depends(get_db)):
    if not request.items:
        raise HTTPException(status_code=400, detail="カートが空です")

    try:
        total_price = sum(item.price * item.quantity for item in request.items)
        new_transaction = Transaction(
            datetime=datetime.now(ZoneInfo("Asia/Tokyo")),
            emp_cd=request.emp_cd,
            store_cd=request.store_cd,
            pos_no=request.pos_no,
            total_amt=total_price
        )
        db.add(new_transaction)

        trd_id = new_transaction.trd_id
        if not trd_id:
            raise HTTPException(status_code=500, detail="取引IDの取得に失敗しました")

        db.commit()
        db.refresh(new_transaction)

        for item in request.items:
            product = db.query(Product).filter(Product.code == item.code).first()
            if not product:
                raise HTTPException(status_code=400, detail=f"商品コード {item.code} が見つかりません")
            
            new_detail = TransactionDetail(
                trd_id=trd_id,
                prd_id=product.PRD_ID,
                prd_code=item.code,
                prd_name=item.name,
                prd_price=item.price
            )
            db.add(new_detail)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return {"trd_id": trd_id, "total_amt": total_price}
