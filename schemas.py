from pydantic import BaseModel
from typing import List
from datetime import datetime


class ItemBase(BaseModel):
    title: str


class ItemCreate(ItemBase):
    qty: int


class Item(ItemBase):
    item_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    address: str


class User(UserBase):
    user_id: int
    items: List[Item] = []

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    item_json: str


class OrderCreate(BaseModel):
    customer_id: int
    order_date: str = datetime.utcnow()
    amount: float


class Order(OrderBase):
    order_id: int

    class Config:
        orm_mode = True


class CartCreate(BaseModel):
    item_id: int
    qty: int
    customer_id: int