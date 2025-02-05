from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, CHAR

Base = declarative_base()

class Product(Base):
    __tablename__ = "m_product_hara"

    PRD_ID = Column(Integer, primary_key=True, autoincrement=True)
    CODE = Column(CHAR(13), unique=True, nullable=False)
    NAME = Column(String(50), nullable=False)
    PRICE = Column(Integer, nullable=False)
