from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.container import get_dependency
from app.service.machine_translator import MachineTranslatorService

router = APIRouter(prefix="/machine-translator", tags=["machine-translator"])


@router.post("/translate")
@inject
async def translate(
    text: str,
    machine_translator: MachineTranslatorService = get_dependency(
        "machine_translator_service"
    ),
):
    return machine_translator.getting_response_file(text)
