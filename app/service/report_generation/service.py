import io
from dataclasses import dataclass

import pandas as pd
from starlette.responses import StreamingResponse

from app.service.text_document import TextDocumentService
from app.service.text_document.enums import Language


@dataclass
class ReportGenerationService:
    text_document_service: TextDocumentService

    @staticmethod
    async def _prepare_response(file):
        response = StreamingResponse(
            file,
            media_type="application/octet-stream",
        )
        response.headers["Content-Disposition"] = (
            "attachment; filename=report.csv"
        )
        return response

    async def generate_csv_report(self, file_url: str, result: str):
        """Создание CSV-файла с результатами."""
        german_documents = (
            await self.text_document_service.get_documents_by_language(
                language=Language.GERMAN
            )
        )
        russian_documents = (
            await self.text_document_service.get_documents_by_language(
                language=Language.RUSSIAN
            )
        )
        data = {
            "file_url": [file_url],
            "german_documents_count": [len(german_documents)],
            "russian_documents_count": [len(russian_documents)],
            "result": [result],
        }
        df = pd.DataFrame(data)

        # Создаем CSV-файл в памяти
        output = io.StringIO()
        df.to_csv(output, index=False)
        output.seek(0)
        return await self._prepare_response(output)
