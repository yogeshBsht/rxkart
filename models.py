import json
from database import Base, SessionLocal, engine
from fastapi import Depends
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import Session, relationship

from schemas import UserCreate, UserUpdate, ItemCreate, OrderCreate


Base.metadata.create_all(bind=engine)


# # Dependency
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
    address = Column(String)
    orders = relationship("Order", back_populates="customer")

    def __str__(self):
        return f"{self.user_id}: {self.email}"

    def set_password(self, password):
        fake_hashed_password = password + "notreallyhashed"
        self.hashed_password = fake_hashed_password

    @classmethod
    def create_user(cls, user: UserCreate):
        db_user = User(email=user.email)
        db_user.set_password(user.password)
        db = SessionLocal()
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        db.close()
        return db_user
    
    @classmethod
    def update_user(cls, user: UserUpdate):
        db = SessionLocal()
        db_user = db.query(cls).filter(cls.email == user.email).first()
        db_user.address = user.address
        db.commit()
        db.close()
        return True
    
    @classmethod
    def get_user_by_email(cls, email: str):
        db = SessionLocal()
        res = db.query(cls).filter(cls.email == email).first()
        db.close()
        return res
    
    @classmethod
    def verify_user(cls, user: UserCreate):
        fake_hashed_password = user.password + "notreallyhashed"
        db_user = cls.get_user_by_email(user.email)
        if db_user.hashed_password == fake_hashed_password:
            return True, db_user.user_id
        return False, None


class Item(Base):
    __tablename__ = "items"

    item_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, unique=True)
    qty = Column(Integer, default=0)
    price = Column(Integer, default=0)

    def __str__(self):
        return f"{self.item_id}: {self.title}"

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
        """Get ordered items for the order_id"""
        db = SessionLocal()
        order = db.query(cls).filter(cls.order_id==order_id).first()
        db.close()
        ordered_items = json.loads(order.ordered_items) if order else {}
        return ordered_items

    @classmethod
    def get_order_for_customer(cls, customer_id: int):
        """Get ordered items for the customer_id"""
        db = SessionLocal()
        order = db.query(cls).filter(cls.customer_id==customer_id).first()
        db.close()
        ordered_items = json.loads(order.ordered_items) if order else {}
        return ordered_items
    
    @classmethod
    def create_order(cls, order: OrderCreate):
        """Create or update the order"""
        db = SessionLocal()
        cust_order = db.query(cls).filter(cls.customer_id==order.customer_id).first()
        kart_item = json.loads(cust_order.ordered_items) if cust_order else {}
        kart_item.update(json.loads(order.item_json))
        if cust_order:
            cust_order.ordered_items = json.dumps(kart_item)
            db.commit()
        else:
            updated_order = cls(customer_id=order.customer_id, ordered_items=json.dumps(kart_item))
            db.add(updated_order)
            db.commit()
            db.refresh(updated_order)
        db.close()
        return True
