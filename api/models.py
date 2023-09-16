from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, JSON

# Create a SQLAlchemy Base model
Base = declarative_base()


# Define database models
class ProductFamily(Base):
    __tablename__ = "product_family"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    product_family_id = Column(Integer, index=True)
    sku = Column(String(255), index=True)
    service_code = Column(String(255), index=True)
    location = Column(String(255))
    region_code = Column(String(255))
    product_attributes = Column(JSON)


class Price(Base):
    __tablename__ = "price"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, index=True)
    pricePerUnit = Column(String(255))
    unit = Column(String(255))
    description = Column(String(255))
