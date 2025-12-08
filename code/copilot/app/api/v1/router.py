from app.api.v1.endpoints import heartbeat, messages
from fastapi import APIRouter

api_v1_router = APIRouter()
api_v1_router.include_router(messages.router, prefix="/messages", tags=["messages"])
api_v1_router.include_router(heartbeat.router, prefix="/health", tags=["health"])
