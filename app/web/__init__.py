from fastapi import APIRouter

from . import text_documents, logical_search


def build_v1_router():
    router = APIRouter(prefix="/v1")
    router.include_router(text_documents.router)
    router.include_router(logical_search.router)
    return router
