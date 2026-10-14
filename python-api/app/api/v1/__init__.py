from fastapi import APIRouter

from app.api.v1 import crud, health, users

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(crud.router)
