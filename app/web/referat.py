from io import BytesIO

from dependency_injector.wiring import inject
from fastapi import APIRouter, File, UploadFile
from starlette.responses import StreamingResponse

from app.container import get_dependency
from app.service.referat.report_generation import ReportGeneration
from app.service.referat.service import ReferatService

router = APIRouter(prefix="/referat", tags=["referat"])


@router.post("/keyword")
@inject
async def keyword(
    file: UploadFile = File(...),
    referat_service: ReferatService = get_dependency(
        "referat_service"
    ),
):
    contents = await file.read()
    text = contents.decode('utf-8')
    return await referat_service.keyword(text)



@router.post("/classic")
@inject
async def keyword(
    file: UploadFile = File(...),
    referat_service: ReferatService = get_dependency(
        "referat_service"
    ),
):
    contents = await file.read()
    text = contents.decode('utf-8')
    return await referat_service.classic(text)


@router.post("/report")
@inject
async def report(
    file: UploadFile = File(...),
    referat_service: ReferatService = get_dependency(
        "referat_service"
    ),
):
    contents = await file.read()
    text = contents.decode('utf-8')
    keyword = await referat_service.keyword(text)
    classic = await referat_service.classic(text)
    return StreamingResponse(
        ReportGeneration.get_report_buffer(keyword, classic),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report.pdf"}
    )

