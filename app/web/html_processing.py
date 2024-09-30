from dependency_injector.wiring import inject
from fastapi import APIRouter, File, UploadFile

from app.container import get_dependency
from app.service.html_processing import HtmlProcessingService

router = APIRouter(prefix="/html", tags=["html"])


@router.post("/process")
@inject
async def process(
    file: UploadFile = File(...),
    html_processing_service: HtmlProcessingService = get_dependency(
        "html_processing_service"
    ),
):
    return await html_processing_service.process_file(file)
