"""
FastAPI приложение для админ-панели IQStocker v2.0

Главный файл админ-панели
"""

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.admin.auth import get_admin
from src.admin.views import analytics, broadcasts, dashboard, lexicon, payments, users
from src.config.logging import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="IQStocker Admin Panel",
    description="Админ-панель для управления IQStocker v2.0",
    version="2.0.0",
)

# Подключаем статические файлы и шаблоны
try:
    app.mount("/static", StaticFiles(directory="src/admin/static"), name="static")
    templates = Jinja2Templates(directory="src/admin/templates")
except Exception:
    # Если директории нет, просто пропускаем
    templates = None


# Регистрация роутеров
app.include_router(
    dashboard.router,
    prefix="/admin",
    tags=["Dashboard"],
    dependencies=[Depends(get_admin)],
)
app.include_router(
    users.router,
    prefix="/admin/users",
    tags=["Users"],
    dependencies=[Depends(get_admin)],
)
app.include_router(
    payments.router,
    prefix="/admin/payments",
    tags=["Payments"],
    dependencies=[Depends(get_admin)],
)
app.include_router(
    analytics.router,
    prefix="/admin/analytics",
    tags=["Analytics"],
    dependencies=[Depends(get_admin)],
)
app.include_router(
    broadcasts.router,
    prefix="/admin/broadcasts",
    tags=["Broadcasts"],
    dependencies=[Depends(get_admin)],
)
app.include_router(
    lexicon.router,
    prefix="/admin/lexicon",
    tags=["Lexicon"],
    dependencies=[Depends(get_admin)],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Главная страница админ-панели"""
    if templates:
        return templates.TemplateResponse("index.html", {"request": {}})
    return HTMLResponse("""
    <html>
        <head>
            <title>IQStocker Admin Panel</title>
        </head>
        <body>
            <h1>IQStocker Admin Panel</h1>
            <p>Админ-панель для управления IQStocker v2.0</p>
            <p><a href="/admin/">Dashboard</a></p>
        </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "admin-panel"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

