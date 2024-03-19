from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles

from .templates import templates
from .database import models
from .database.db import engine
from .routers.url import url_router
from .routers.user import router

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="scissor"
)

app.include_router(url_router)
app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", tags=["HomePage"])
async def homepage(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return templates.TemplateResponse("http_error.html",
                                      {"request": request, "status_code": exc.status_code, "exc": exc})


@app.exception_handler(404)
async def http_exception_handler(request: Request, exc: Exception):
    return templates.TemplateResponse("http_error.html", {"request": request, "status_code": 404, "exc": exc})

