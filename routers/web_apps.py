
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from core.auth_handler import get_current_username

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    """Botのポータル画面を表示"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/star-whale", response_class=HTMLResponse)
async def star_whale_page():
    """星くじらWeb体験版ページ"""
    try:
        with open("static/star_whale.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/owl", response_class=HTMLResponse, dependencies=[Depends(get_current_username)])
async def owl_page():
    """フクロウ教授のWebアプリ（要認証）"""
    try:
        with open("static/owl.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/capybara", response_class=HTMLResponse)
async def capybara_page():
    """カピバラニュース（認証なし）"""
    try:
        with open("static/capybara.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)
