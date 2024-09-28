from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.container import get_dependency
from app.service.neural_method import NeuralMethodService

router = APIRouter(prefix="/neural-method", tags=["neural-method"])


@router.post("/create-model")
@inject
async def create_model(
    neural_method_service: NeuralMethodService = get_dependency(
        "neural_method_service"
    ),
):
    await neural_method_service.create_model()


@router.post("/predict")
@inject
async def predict_language(
    text: list[str],
    neural_method_service: NeuralMethodService = get_dependency(
        "neural_method_service"
    ),
):
    return await neural_method_service.predict(text)
