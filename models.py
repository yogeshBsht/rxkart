import json
from database import Base, SessionLocal, engine
from datetime import datetime
from fastapi import Depends
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Float
from sqlalchemy.orm import Session, relationship

from schemas import UserCreate, UserUpdate, ItemCreate, OrderCreate, CartCreate


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
    name = Column(String, default="guest")
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    address = Column(String)
    carts = relationship("Cart", back_populates="customer")
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
    price = Column(Integer, default=0)
    carts = relationship("Cart", back_populates="items")

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


class Cart(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey('items.item_id'))
    qty = Column(Integer)
    customer_id = Column(Integer, ForeignKey('users.user_id'))
    order_id = Column(Integer, ForeignKey('orders.order_id'), default=None)
    orders = relationship("Order", back_populates="carts")
    items = relationship("Item", back_populates="carts")
    customer = relationship("User", back_populates="carts")

    def __str__(self):
        return f"OrderId-{self.id}, ItemId-{self.item_id}, CustomerId-{self.customer_id}"

    @classmethod
    def get_cart_items_for_customer(cls, customer_id: int):
        """Get cart items for the customer_id"""
        db = SessionLocal()
        cart = db.query(cls, Item).filter(cls.item_id==Item.item_id).filter(cls.customer_id==customer_id)\
            .filter(cls.order_id.is_(None)).all()
        db.close()
        cart_items = []
        if cart:
            for crt,itm in cart:
                cart_items.append((itm.title, crt.qty, itm.price, crt.qty*itm.price))
        return cart_items
    
    @classmethod
    def create_entry(cls, entry: CartCreate):
        """Create or update the order"""
        db = SessionLocal()
        cust_order = db.query(cls).filter(cls.customer_id==entry.customer_id).filter(cls.item_id==entry.item_id).first()
        if cust_order:
            cust_order.qty = entry.qty
            db.commit()
        else:
            new_entry = cls(customer_id=entry.customer_id, item_id=entry.item_id, qty=entry.qty)
            db.add(new_entry)
            db.commit()
            db.refresh(new_entry)
        db.close()
        return True
    
    @classmethod
    def update_cart_items_for_customer(cls, customer_id: int):
        """Update cart items for the customer_id after checkout"""
        db = SessionLocal()
        cart = db.query(cls, Item).filter(cls.item_id==Item.item_id).filter(cls.customer_id==customer_id).all()
        db.close()
        cart_items = []
        if cart:
            for crt,itm in cart:
                cart_items.append((itm.title, crt.qty, itm.price, crt.qty*itm.price))
        return cart_items
    
    @classmethod
    def update_cart_orderId_for_customer(cls, customer_id: int, order_id: int):
        """Update order_id of cart items for the customer_id after checkout"""
        db = SessionLocal()
        cart = db.query(cls).filter(cls.customer_id==customer_id).filter(cls.order_id.is_(None)).all()
        if cart:
            for crt_item in cart:
                print("hi")
                crt_item.order_id = order_id
            db.commit()
        db.close()
        return True


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    order_date = Column(DateTime, default=datetime.utcnow())
    amount = Column(Float)
    customer_id = Column(Integer, ForeignKey('users.user_id'))
    customer = relationship("User", back_populates="orders")
    carts = relationship("Cart", back_populates="orders")

    def __str__(self):
        return f"OrderId-{self.order_id}, CustomerId-{self.customer_id}"

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
        orders = db.query(cls).filter(cls.customer_id==customer_id).all()
        orders_dict = {}
        for order in orders:
            items_in_order = [
                {
                    "title": cart.items.title, 
                    "qty": cart.qty,
                    "price": cart.items.price,
                    "total_price": cart.items.price*cart.qty 
                } for cart in order.carts
            ]
            if items_in_order:
                orders_dict.update({order.order_id: items_in_order})
        db.close()
        return orders_dict
    
    @classmethod
    def create_order(cls, order: OrderCreate):
        """Create order"""
        db = SessionLocal()
        new_order = cls(customer_id=order.customer_id, amount=order.amount)
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        new_order_id = new_order.order_id
        db.close()
        Cart.update_cart_orderId_for_customer(order.customer_id, new_order_id)
        return True
