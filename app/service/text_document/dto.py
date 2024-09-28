from typing import Optional

from beanie import Document
from pydantic import Field


class TextDocument(Document):
    name: str
    text: str
    language: Optional[str] = Field(default="ru")

    class Settings:
        name = "text-document"
