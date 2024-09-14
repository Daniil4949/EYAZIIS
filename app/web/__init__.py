from fastapi import APIRouter

from . import calculate_weight_coefficient, logical_search, text_documents


def build_v1_router():
    router = APIRouter(prefix="/v1")
    router.include_router(text_documents.router)
    router.include_router(logical_search.router)
    router.include_router(calculate_weight_coefficient.router)
    return router
