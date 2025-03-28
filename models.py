from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP

# ベースクラスを定義
Base = declarative_base()

# 商品テーブル
class Product(Base):
    __tablename__ = 'm_product_hara'

    PRD_ID = Column(Integer, primary_key=True)  # 仕様書には AUTO_INCREMENT 記載なし
    code = Column(String(13), unique=True, nullable=False)  # CHAR(13) に修正
    name = Column(String(50), nullable=False)  # VARCHAR(50) に修正
    price = Column(Integer, nullable=False)


# 取引テーブル
class Transaction(Base):
    __tablename__ = "m_transactions_hara"

    trd_id = Column(Integer, primary_key=True, autoincrement=True)  # ID名を仕様に合わせる
    datetime = Column(TIMESTAMP, nullable=False)  # created_at → datetime に変更
    emp_cd = Column(String(10), nullable=False, default="9999999999")  # レジ担当者コード
    store_cd = Column(String(5), nullable=False, default="30")  # 店舗コード
    pos_no = Column(String(3), nullable=False, default="90")  # POS機ID
    total_amt = Column(Integer, nullable=False, default=0)  # total → total_amt に変更

# 取引詳細テーブル
class TransactionDetail(Base):
    __tablename__ = 'm_transaction_details_hara'

    dtl_id = Column(Integer, primary_key=True, autoincrement=True)
    trd_id = Column(Integer, ForeignKey('m_transactions_hara.trd_id'), nullable=False)  # 修正
    prd_id = Column(Integer, ForeignKey('m_product_hara.PRD_ID'), nullable=False)  # 商品ID追加
    prd_code = Column(String(13), nullable=False)  # CHAR(13) に修正
    prd_name = Column(String(50), nullable=False)  # VARCHAR(50) に修正
    prd_price = Column(Integer, nullable=False)
