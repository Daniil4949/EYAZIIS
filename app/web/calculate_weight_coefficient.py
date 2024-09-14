from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.container import get_dependency
from app.service.calculate_weight_coefficient.service import (
    WeightCoefficientService,
)

router = APIRouter(
    prefix="/calculate-weight-coefficient",
    tags=["calculate-weight-coefficient"],
)


@router.get("/", response_model=dict[str, dict[str, float]])
@inject
async def calculate_weight_coefficient(
    weight_coefficient_service: WeightCoefficientService = get_dependency(
        "weight_coefficient_service"
    ),
):
    return await weight_coefficient_service.calculate_tfidf()
