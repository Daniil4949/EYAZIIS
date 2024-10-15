from dependency_injector.wiring import inject
from fastapi import APIRouter, File, UploadFile

from app.container import get_dependency
from app.service.language_detection.neural_and_ngramm_method import (
    NgrammAndNeuralMethodService,
)

router = APIRouter(prefix="/ngramm-method", tags=["ngramm-method"])


@router.post("/create-model")
@inject
async def create_model(
    ngramm_method_service: NgrammAndNeuralMethodService = get_dependency(
        "ngramm_method_service"
    ),
):
    await ngramm_method_service.create_model()


@router.post("/predict")
@inject
async def predict_language(
    file: UploadFile = File(...),
    ngramm_method_service: NgrammAndNeuralMethodService = get_dependency(
        "ngramm_method_service"
    ),
):
    return await ngramm_method_service.predict(file)
