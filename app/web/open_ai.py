from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.container import get_dependency
from app.service.open_ai_service import OpenAIService

router = APIRouter(prefix="/open-ai", tags=["open-ai"])


@router.get("/")
@inject
async def get_open_ai_service(
    text: str,
    open_ai_service: OpenAIService = get_dependency("open_ai_service"),
):
    return await open_ai_service.getting_response_from_open_ai(text)
