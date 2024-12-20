from dataclasses import dataclass
from typing import Optional

from app.service.text_document.dto import TextDocument
from app.service.text_document.enums import Language


@dataclass
class TextDocumentRepository:

    @staticmethod
    async def find_by_name(name: str) -> Optional[TextDocument]:
        document = await TextDocument.find_one(TextDocument.name == name)
        return document

    @staticmethod
    async def get_all() -> list[TextDocument]:
        documents = await TextDocument.find_all().to_list()
        return documents

    @staticmethod
    async def create_document(data: TextDocument) -> Optional[TextDocument]:
        document = await TextDocument.insert_one(data)
        return document

    @staticmethod
    async def delete_document(name: str) -> None:
        await TextDocument.find_one(TextDocument.name == name).delete()

    @staticmethod
    async def get_document_by_language(
        language: Language,
    ) -> list[TextDocument]:
        documents = await TextDocument.find(
            TextDocument.language == language
        ).to_list()
        return documents
