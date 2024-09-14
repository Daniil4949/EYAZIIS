from dependency_injector.wiring import inject
from fastapi import APIRouter

from app.container import get_dependency
from app.service.text_document import TextDocument, TextDocumentService

router = APIRouter(prefix="/text-documents", tags=["text-documents"])


@router.get("/", response_model=list[TextDocument])
@inject
async def get_text_documents(text_document_service: TextDocumentService = get_dependency("text_document_service")):
    return await text_document_service.get_all_documents()


@router.get("/{document_name}", response_model=TextDocument)
@inject
async def get_text_document_by_name(document_name: str, text_document_service: TextDocumentService = get_dependency(
    "text_document_service")):
    return await text_document_service.get_document(document_name=document_name)


@router.post("/create-document", response_model=TextDocument)
@inject
async def create_text_document(data: TextDocument,
                               text_document_service: TextDocumentService = get_dependency("text_document_service")):
    return await text_document_service.create_document(data=data)


@router.delete("/{document_name}")
@inject
async def delete_text_document(document_name: str,
                               text_document_service: TextDocumentService = get_dependency("text_document_service")):
    return await text_document_service.delete_document(document_name=document_name)
