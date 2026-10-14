from fastapi import APIRouter

from app.core.config import get_settings
from app.domain.schemas.monitor import Monitor

router = APIRouter(tags=["Monitor"])


@router.get("/", response_model=Monitor, summary="Show the name and version of the server")
def health_check() -> Monitor:
    settings = get_settings()
    return Monitor(name=settings.name, version=settings.version)
