from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import json
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from models import User, Item, ItemCreate, Order


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

templates = Jinja2Templates(directory="templates")


# # Dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

@app.get("/register", response_class=HTMLResponse)
def get_register_form(request:Request):
    return templates.TemplateResponse("register.html", {"request": request, "text": "register"})


@app.post("/register", response_model=schemas.User)
def create_user(email: str = Form(...), password: str = Form(...)):
    user = schemas.UserCreate(email=email, password=password)
    db_user = User.get_user_by_email(email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return User.create_user(user=user)


@app.get("/login", response_class=HTMLResponse)
def login(request:Request):
    return templates.TemplateResponse("register.html", {"request": request, "text": "login"})


@app.post("/login", response_model=dict)
def login_user(request:Request, email: str = Form(...), password: str = Form(...)):
    user = schemas.UserCreate(email=email, password=password)
    is_used_verified = User.verify_user(user)
    if not is_used_verified:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return templates.TemplateResponse("index.html", {"request": request, "mykart": Item.get_items()})


@app.get("/mykart/{user_id}", response_model=dict)
def get_user_kart(request:Request, user_id: int):
    return templates.TemplateResponse("mykart.html", {
        "request": request,
        "user_id": user_id, 
        "mykart": Order.get_order_for_customer(user_id)
    })


@app.get("/add_to_kart/{user_id}", response_class=HTMLResponse)
def add_item_to_kart(request:Request, user_id: int):
    error = None
    return templates.TemplateResponse("home.html", {
        "request": request, 
        "medicines": Item.get_items(),
        "error": error
    })  


@app.post("/add_to_kart/{user_id}", response_class=HTMLResponse)
def add_item_to_kart(request:Request, user_id: int, medicine: str = Form(...), qty: int = Form(...)):
# def add_item_to_kart(request:Request, user_id: int, qty: int = Form(...)):
    item = schemas.OrderCreate(item_json=json.dumps({medicine: qty}), customer_id=user_id)
    error = None
    try: 
        is_created = Order.create_order(item)
    except:
        error = "Item already exists" 
    return templates.TemplateResponse("home.html", {"request": request, "error": error})   


@app.get("/add_item", response_class=HTMLResponse)
def add_item(request:Request, error=None): 
    return templates.TemplateResponse("add_item.html", {"request": request, "error": None})   


@app.post("/add_item", response_class=HTMLResponse)
def add_item(request:Request, title: str = Form(...), qty: int = Form(...)):
    item = schemas.ItemCreate(title=title, qty=qty)
    error = None
    try: 
        is_created = Item.create_item(item=item)
    except:
        error = "Item already exists" 
    return templates.TemplateResponse("add_item.html", {"request": request, "error": error})   


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=5049)

