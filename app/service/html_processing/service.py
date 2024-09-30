from dataclasses import dataclass

from bs4 import BeautifulSoup
from fastapi import File, HTTPException


@dataclass
class HtmlProcessingService:

    async def process_file(self, file: File) -> str:
        if not file.filename.endswith(".html"):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an HTML file.",
            )
        try:
            content = await file.read()
            result = self._parse_html(content.decode("utf-8"))
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error processing file: {str(e)}"
            )
        return result

    @staticmethod
    def _parse_html(html_content: str) -> str:
        """
        Извлекает текст из HTML-документа.

        :param html_content: строка, содержащая HTML-код.
        :return: извлеченный текст.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        return soup.get_text(strip=True)
