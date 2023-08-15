import json
from database import Base, SessionLocal, engine
from fastapi import Depends
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Session, relationship

from schemas import UserCreate, ItemCreate, OrderCreate


Base.metadata.create_all(bind=engine)


# Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    orders = relationship("Order", back_populates="customer")

    def __str__(self):
        return f"{self.user_id}: {self.email}"

    @classmethod
    def create_user(cls, user: UserCreate):
        fake_hashed_password = user.password + "notreallyhashed"
        db_user = User(email=user.email, hashed_password=fake_hashed_password)
        db = SessionLocal()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return db_user
    
    @classmethod
    def get_user_by_email(cls, email: str):
        db = SessionLocal()
        res = db.query(User).filter(User.email == email).first()
        db.close()
        return res
    
    @classmethod
    def verify_user(cls, user: UserCreate):
        fake_hashed_password = user.password + "notreallyhashed"
        db_user = cls.get_user_by_email(user.email)
        if db_user.hashed_password == fake_hashed_password:
            return True
        return False


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, unique=True)
    qty = Column(Integer, default=0)

    @classmethod
    def get_items(cls, skip: int = 0, limit: int = 100):
        db = SessionLocal()
        items = db.query(Item).offset(skip).limit(limit).all()
        db.close()
        return items
    
    @classmethod
    def create_item(cls, item: ItemCreate):
        db_item = Item(title=item.title, qty=item.qty)
        db = SessionLocal()
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.close()
        return item


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    ordered_items = Column(JSON)
    customer_id = Column(Integer, ForeignKey('users.user_id'))
    customer = relationship("User", back_populates="orders")

    def __str__(self):
        return f"OrderId-{self.order_id}, CustomerId-{self.customer_id}, {self.ordered_items}"

    @classmethod
    def get_order_by_id(cls, order_id: int):
        db = SessionLocal()
        order = db.query(cls).filter(cls.order_id==order_id).all()
        db.close()
        ordered_items = json.loads(order[0].ordered_items) if order else {}
        return ordered_items

    @classmethod
    def get_order_for_customer(cls, customer_id: int):
        db = SessionLocal()
        order = db.query(cls).filter(cls.customer_id==customer_id).all()
        db.close()
        ordered_items = json.loads(order[0].ordered_items) if order else {}
        return ordered_items
    
    @classmethod
    def create_order(cls, order: OrderCreate):
        kart_item = cls.get_order_for_customer(order.customer_id)
        kart_item.update(order.item_json)
        db = SessionLocal()
        db.add(kart_item)
        db.commit()
        db.refresh(kart_item)
        db.close()
        return True
