from dataclasses import dataclass

from app.service.text_document import TextDocument
from app.service.text_document.repository import TextDocumentRepository


@dataclass
class TextDocumentService:
    text_document_repository: TextDocumentRepository

    async def get_all_documents(self) -> list[TextDocument]:
        return await self.text_document_repository.get_all()

    async def get_document(self, document_name: str) -> TextDocument:
        return await self.text_document_repository.find_by_name(name=document_name)

    async def create_document(self, data: TextDocument) -> TextDocument:
        return await self.text_document_repository.create_document(data=data)

    async def delete_document(self, document_name: str) -> None:
        return await self.text_document_repository.delete_document(name=document_name)
