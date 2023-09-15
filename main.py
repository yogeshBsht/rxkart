import json
from fastapi import FastAPI, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import schemas
from models import User, Item, Cart, Order
from payment import create_payment


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

templates = Jinja2Templates(directory="templates")


@app.middleware("http")
async def validate_user(request: Request, call_next):
    print(request.session)
    response = await call_next(request)
    return response


@app.get("/register", response_class=HTMLResponse)
def get_registration_page(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "user_email": None,
        "text": "register"
    })


@app.post("/register", response_model=schemas.User)
def register_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = schemas.UserCreate(email=email, password=password)
    db_user = User.get_user_by_email(email=user.email)
    if not db_user:
        User.create_user(user=user)
    redirect_url = request.url_for('get_login_page')    
    return RedirectResponse(redirect_url)


@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
def get_login_page(request: Request):
    return templates.TemplateResponse("register.html", {
        "request": request,
        "user_email": None,
        "text": "login"
    })


@app.post("/login", response_model=dict)
def login_user(request: Request, email: str = Form(...), password: str = Form(...)):
    user = schemas.UserCreate(email=email, password=password)
    is_used_verified, user_id = User.verify_user(user)
    if not is_used_verified:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    
    request.session["session_id"] = user_id, email
    redirect_url = request.url_for('get_user_kart')    
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/logout")
def logout(request: Request):
    if request.session.get("session_id"):
        request.session.pop("session_id")
    redirect_url = request.url_for('get_login_page')    
    return RedirectResponse(redirect_url)


@app.get("/profile", response_model=dict)
def get_user_profile(request: Request):
    user_id, email = request.session.get("session_id", [None, None])
    if not user_id:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url)
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "user_email": email,
        "user": User.get_user_by_email(email)
    })


@app.get("/mykart", response_model=dict)
def get_user_kart(request: Request):
    user_id, email = request.session.get("session_id", [None, None])
    if not user_id:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url)
    return templates.TemplateResponse("mykart.html", {
        "request": request,
        "user_email": email,
        "mykart": Cart.get_cart_items_for_customer(user_id)
    })


@app.get("/add_to_kart", response_class=HTMLResponse)
def get_add_item_to_kart_page(request: Request):
    user_id, email = request.session.get("session_id", [None, None])
    if not user_id:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user_email": email,
        "medicines": Item.get_items()
    })


@app.get("/myorders", response_model=dict)
def get_user_orders(request: Request):
    user_id, email = request.session.get("session_id", [None, None])
    if not user_id:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url)
    return templates.TemplateResponse("myorders.html", {
        "request": request,
        "user_email": email,
        "orders": Order.get_order_for_customer(user_id)
    })


@app.post("/add_to_kart", response_class=HTMLResponse)
def add_item_to_kart(request: Request, medicine: str = Form(...), qty: int = Form(...)):
    user_id, email = request.session.get("session_id", [None, None])
    if not user_id:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url)
    cart_entry = schemas.CartCreate(
        item_id=int(medicine),
        qty=qty,
        customer_id=user_id
    )
    is_created = Cart.create_entry(cart_entry)
    return templates.TemplateResponse("home.html", {
        "request": request,
        "user_email": email,
        "medicines": Item.get_items()
    })


@app.get("/checkout", response_model=dict)
def get_checkout_page(request: Request):
    user_id, email = request.session.get("session_id", [None, None])
    if not user_id:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url)
    return templates.TemplateResponse("checkout.html", {
        "request": request,
        "user_email": email,
        "mykart": Cart.get_cart_items_for_customer(user_id)
    })


@app.post("/checkout", response_model=dict)
async def process_checkout(request: Request, amount: int = Form(...)):
    user_id, email = request.session.get("session_id", [None, None])
    if not user_id:
        redirect_url = request.url_for('get_login_page')    
        return RedirectResponse(redirect_url)

    resp = await create_payment(amount)
    if resp and resp.get("clientSecret"):
        order = schemas.OrderCreate(amount=amount, customer_id=user_id)
        Order.create_order(order)
    redirect_url = request.url_for('get_user_kart')    
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@app.get("/add_item", response_class=HTMLResponse)
def add_item(request: Request):
    return templates.TemplateResponse("add_item.html", {"request": request, "error": None})


@app.post("/add_item", response_class=HTMLResponse)
def add_item(request: Request, title: str = Form(...), qty: int = Form(...)):
    item = schemas.ItemCreate(title=title, qty=qty)
    error = None
    try:
        is_created = Item.create_item(item=item)
    except:
        error = "Item already exists"
    return templates.TemplateResponse("add_item.html", {"request": request, "error": error})


app.add_middleware(SessionMiddleware, secret_key="some-random-string")
# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=5049)
