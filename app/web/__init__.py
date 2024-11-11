from fastapi import APIRouter

from . import (
    alphabet_method,
    calculate_weight_coefficient,
    html_processing,
    logical_search,
    neural_method,
    ngramm_method,
    open_ai,
    speech_synthesis,
    text_documents,
)


def build_v1_router():
    router = APIRouter(prefix="/v1")
    router.include_router(text_documents.router)
    router.include_router(logical_search.router)
    router.include_router(calculate_weight_coefficient.router)
    router.include_router(open_ai.router)
    router.include_router(neural_method.router)
    router.include_router(ngramm_method.router)
    router.include_router(alphabet_method.router)
    router.include_router(html_processing.router)
    router.include_router(speech_synthesis.router)
    return router
