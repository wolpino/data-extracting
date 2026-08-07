from fastapi import APIRouter

from data_extracting_backend.api.v1 import orders

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(orders.router)
