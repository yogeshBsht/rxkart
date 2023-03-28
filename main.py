from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

templates = Jinja2Templates(directory="templates")

medicine_list = [
    {"id":1, "name":"paracetamol", "qty":10},
    {"id":2, "name":"cough_syrup", "qty":20},
    {"id":3, "name":"novartis", "qty":5}
]

mykart = {}

@app.get("/", response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse("home.html", {"request": request, "medicines":medicine_list})

@app.post("/mykart", response_class=HTMLResponse)
async def index(request:Request, medicine:str, qty:int = 1):
    mykart.setdefault(medicine, qty)
    return templates.TemplateResponse("index.html", {"request": request, "mykart":mykart})


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=5049)

