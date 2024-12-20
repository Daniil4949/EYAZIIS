from dependency_injector.wiring import inject
from fastapi import APIRouter, File, UploadFile

from app.container import get_dependency
from app.service.alphabet_method import AlphabetMethodService

router = APIRouter(prefix="/alphabet-method", tags=["alphabet-method"])


@router.post("/predict")
@inject
async def predict_language(
    file: UploadFile = File(...),
    alphabet_method_service: AlphabetMethodService = get_dependency(
        "alphabet_method_service"
    ),
):
    return await alphabet_method_service.predict(file)
