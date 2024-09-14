from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.container import get_dependency
from app.service.logical_search.service import LogicalSearchService
from app.service.text_document import TextDocument

router = APIRouter(prefix="/logical-search", tags=["logical-search"])


@router.get("/", response_model=list[TextDocument])
@inject
async def logical_search(
    expression: str,
    logical_search_service: LogicalSearchService = get_dependency(
        "logical_search_service"
    ),
):
    return await logical_search_service.search(expression)
