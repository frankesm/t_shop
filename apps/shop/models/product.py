from sqlalchemy import Column, Integer, String, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base


class Product(Base):
    __tablename__ = "shop.products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    unit = Column(String(255), nullable=False, default="Unidades")
    amount = Column(Integer, nullable=False)
    buy_cost = Column(DECIMAL(20, 2), nullable=False)
    buy_id = Column(Integer, ForeignKey("shop.buy.id"), nullable=False)

    buy = relationship("Buy", back_populates="products")

    def __repr__(self):
        return f"{self.code} - {self.name}"
