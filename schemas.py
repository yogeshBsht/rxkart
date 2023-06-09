from pydantic import BaseModel
from typing import List, Dict


class ItemBase(BaseModel):
    title: str


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    item_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    user_id: int
    items: List[Item] = []

    class Config:
        orm_mode = True


class OrderBase(BaseModel):
    item_json: Dict[int,int]


class OrderCreate(OrderBase):
    pass


class Order(OrderBase):
    order_id: int

    class Config:
        orm_mode = True