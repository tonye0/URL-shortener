from fastapi import Request, Response, HTTPException, Depends, APIRouter, status, Form
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse

from fastapi_simple_rate_limiter import rate_limiter

from typing import Annotated
from validators import url as validate_url
from sqlalchemy.orm import Session

from ..templates import templates
from ..utils import generate_short_url, generate_qr_code
from ..database.db import get_db
from ..schemas.url import UrlResponse
from ..database.models import URL, Click
from .user import get_current_user

url_router = APIRouter(
    tags=["URLs"]
)


@url_router.get("/urls", response_class=HTMLResponse, response_model=UrlResponse)
@rate_limiter(limit=10, seconds=60)
async def all_urls(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    urls = db.query(URL).filter(URL.user_id == user.get("id")).all()

    return templates.TemplateResponse("history.html", {"request": request, "urls": urls})


@url_router.get("/url", response_class=HTMLResponse)
async def index(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse({"request": request}, "short.html")



@url_router.post("/shorten-long-url")

async def shorten_long_url(
        response: Response,
        request: Request,
        long_url: Annotated[str, Form()],
        custom_url: str = Form(None),
        db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    if not validate_url(long_url):
        raise HTTPException(status_code=400, detail="URL is not valid")

    if custom_url:
        existing_url = db.query(URL).filter(URL.short_url == custom_url).first()
        if existing_url:
            raise HTTPException(status_code=400, detail="Custom link already in use")
        short_url = custom_url
    else:
        short_url = generate_short_url()
    
    print("Short URL:", short_url)

    url_link = URL()
    url_link.long_url = long_url
    url_link.short_url = short_url
    url_link.clicks = 0
    url_link.user_id = user.get("id")

    db.add(url_link)
    db.commit()
    db.refresh(url_link)

    return templates.TemplateResponse({"request": request, "url": short_url}, "shortened.html")


@url_router.get("/download-qrcode")
@rate_limiter(limit=10, seconds=60)
async def download_qr_code_form(request: Request):
    return templates.TemplateResponse("download_qrcode.html", {"request": request})


@url_router.get("/qrcode")
async def download_qr_code(request: Request, url: str):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    qr_code_path = generate_qr_code(url)
    return FileResponse(
        qr_code_path,
        media_type="image/png",
        headers={"Content-Disposition": "attachment; filename=qr_code.png"}
    )


@url_router.get("/analytics", response_class=HTMLResponse)
@rate_limiter(limit=10, seconds=60)
async def show_analytics_form(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("clicks.html", {"request": request})


@url_router.post("/analytic")
@rate_limiter(limit=10, seconds=60)
async def get_analytics(request: Request, short_url: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    db_url = db.query(URL).filter(URL.short_url == short_url).first()
    if db_url:
        return templates.TemplateResponse(
            "analytics.html",
            {
                "request": request,
                "short_url": short_url,
                "clicks": db_url.clicks,
            }
        )
    else:
        raise HTTPException(status_code=404, detail="Short URL not found")


@url_router.post("/delete/{url_id}")
async def delete_url(request: Request, url_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse("/user/login", status_code=status.HTTP_302_FOUND)

    urls = db.query(URL).filter(URL.user_id == user.get("id")).all()

    url_to_delete = db.query(URL).filter(URL.id == url_id).first()

    if not url_to_delete:
        raise HTTPException(status_code=404, detail="URL not found")

    db.delete(url_to_delete)
    db.commit()
    return RedirectResponse("/urls/", status_code=status.HTTP_303_SEE_OTHER)


@url_router.get("/{short_url}")
async def redirect_to_long_url(short_url: str, db: Session = Depends(get_db)):
    original_url = db.query(URL).filter(URL.short_url == short_url).first()
    if original_url:
        original_url.clicks += 1
        clicks = Click(url_id=original_url.id)
        db.add(clicks)
        db.commit()
        db.refresh(clicks)
        return RedirectResponse(original_url.long_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    else:
        raise HTTPException(status_code=404, detail="URL not found")



    
    
