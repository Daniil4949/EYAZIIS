from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.container import get_dependency
from app.service.speech_synthesis.dto import SpeechSynthesisDto
from app.service.speech_synthesis.service import SpeechSynthesisService

router = APIRouter(prefix="/speech-synthesis", tags=["speech-synthesis"])


@router.post("/")
@inject
async def speech_synthesis(
    speech_synthesis_parameters: SpeechSynthesisDto,
    speech_synthesis_service: SpeechSynthesisService = get_dependency(
        "speech_synthesis_service"
    ),
):
    speech_synthesis_service.pronounce_text(data=speech_synthesis_parameters)
