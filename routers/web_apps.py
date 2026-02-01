
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def index():
    """Botのポータル画面を表示"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/beaver", response_class=HTMLResponse)
async def beaver_page():
    """ビーバーのタスク管理ダム（認証なし）"""
    try:
        with open("static/beaver.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
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

@router.get("/owl", response_class=HTMLResponse)
async def owl_page():
    """フクロウ教授のWebアプリ（認証なし）"""
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

@router.get("/bat", response_class=HTMLResponse)
async def bat_page():
    """コウモリの監視塔（認証なし）"""
    try:
        with open("static/bat.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/fox", response_class=HTMLResponse)
async def fox_page():
    """キツネの動画要約（認証なし）"""
    try:
        with open("static/fox.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/frog", response_class=HTMLResponse)
async def frog_page():
    """お天気ケロくん（認証なし）"""
    try:
        with open("static/frog.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/mole", response_class=HTMLResponse)
async def mole_page():
    """もぐら駅長の時刻表（認証なし）"""
    try:
        with open("static/mole.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/penguin", response_class=HTMLResponse)
async def penguin_page():
    """ペンギンのコンシェルジュ（認証なし）"""
    try:
        with open("static/penguin.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/voidoll", response_class=HTMLResponse)
async def voidoll_page():
    """Voidollのチャット（認証なし）"""
    try:
        with open("static/voidoll.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/alpaca", response_class=HTMLResponse)
async def alpaca_page():
    """アルパカのまつエクサロン（認証なし）"""
    try:
        with open("static/alpaca.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/flamingo", response_class=HTMLResponse)
async def flamingo_page():
    """フラミンゴ先生の姿勢チェック（認証なし）"""
    try:
        with open("static/flamingo.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/butterfly", response_class=HTMLResponse)
async def butterfly_page():
    """Butterfly (Checko) パーソナルカラー・骨格診断（認証なし）"""
    try:
        with open("static/butterfly.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/squirrel", response_class=HTMLResponse)
async def squirrel_page():
    """リスのほっぺたどんぐりゲーム（認証なし）"""
    try:
        with open("static/squirrel.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)

@router.get("/fish", response_class=HTMLResponse)
async def fish_page():
    """カラフルお魚のお部屋水族館（認証なし）"""
    try:
        with open("static/fish.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)


@router.get("/butsubutsu", response_class=HTMLResponse)
async def butsubutsu_page():
    """英語嫌いのブツブツアプリ（認証なし）"""
    try:
        with open("static/butsubutsu.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"})
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Page Not Found</h1>", status_code=404)
