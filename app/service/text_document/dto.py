from beanie import Document


class TextDocument(Document):
    name: str
    text: str
    link: str | None = None

    class Settings:
        name = "text-document"
