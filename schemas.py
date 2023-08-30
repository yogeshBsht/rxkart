from pydantic import BaseModel
from typing import List, Dict


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


class OrderCreate(OrderBase):
    customer_id: int


class Order(OrderBase):
    order_id: int

    class Config:
        orm_mode = True