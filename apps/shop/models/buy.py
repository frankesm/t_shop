from sqlalchemy import Column, Integer, Date, DECIMAL, String
from sqlalchemy.orm import relationship

from config.database import Base


class Buy(Base):
    __tablename__ = "shop.buy"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    code = Column(String(255))
    other_cost = Column(DECIMAL(20, 2), nullable=False, default=0)
    transportation_cost = Column(DECIMAL(20, 2), nullable=False, default=0)

    products = relationship(
        "Product",
        back_populates="buy",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"{self.date} - {self.code}"
