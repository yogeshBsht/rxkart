from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import SessionLocal, engine


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

templates = Jinja2Templates(directory="templates")

# # medicine_list = [
# #     {"id":1, "name":"paracetamol", "qty":10},
# #     {"id":2, "name":"cough_syrup", "qty":20},
# #     {"id":3, "name":"novartis", "qty":5}
# # ]


models.Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/register", response_class=HTMLResponse)
def get_register_form(request:Request):
    return templates.TemplateResponse("register.html", {"request": request, "text": "register"})
    # return HTMLResponse(content=html_content, status_code=200)


@app.post("/register", response_model=schemas.User)
# def create_user(user: schemas.UserCreate = Form(...), db: Session = Depends(get_db)):
# def create_user(email: Annotated[str,Form()], password: Annotated[str,Form()], db: Session = Depends(get_db)):
def create_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = schemas.UserCreate(email=email, password=password)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/login", response_class=HTMLResponse)
def get_register_form(request:Request):
    return templates.TemplateResponse("register.html", {"request": request, "text": "login"})


@app.post("/login", response_model=dict)
def login_user(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = schemas.UserCreate(email=email, password=password)
    is_used_verified = crud.verify_user(db, user)
    if not is_used_verified:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": "my_access_token"}


# @app.post("/users/", response_model=schemas.User)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
#     db_user = crud.get_user_by_email(db, email=user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     return crud.create_user(db=db, user=user)


# @app.get("/users/", response_model=List[schemas.User])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users


# @app.get("/users/{user_id}", response_model=schemas.User)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user


# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=List[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items


# @app.post("/items/", response_model=schemas.Item)
# def create_item(item: schemas.ItemCreate, db: Session = Depends(get_db)):
#     return crud.create_item(db=db, item=item)


# @app.post("/order/", response_model=schemas.Order)
# def create_item(order: schemas.OrderCreate, db: Session = Depends(get_db)):
#     return crud.create_order(db=db, order=order)


# @app.get("/order/", response_model=List[schemas.Order])
# def read_order(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     orders = crud.get_orders(db, skip=skip, limit=limit)
#     return orders

# mykart = {}

# @app.get("/", response_class=HTMLResponse)
# async def root(request:Request):
#     return templates.TemplateResponse("home.html", {"request": request, "medicines":medicine_list})

# @app.get("/mykart", response_class=HTMLResponse)
# async def index(request:Request, medicine:str, qty:int = 1):
#     mykart.update({medicine: qty})
#     return templates.TemplateResponse("index.html", {"request": request, "mykart":mykart})


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=5049)

