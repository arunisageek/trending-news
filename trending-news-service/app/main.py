from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api.errors import register_exception_handlers
from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.trending import router as trending_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.session import engine

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    default_response_class=JSONResponse,
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(events_router, prefix="/api/v1")
app.include_router(trending_router, prefix="/api/v1")


@app.on_event("startup")
def startup() -> None:
    if settings.create_tables_on_startup:
        Base.metadata.create_all(bind=engine)
