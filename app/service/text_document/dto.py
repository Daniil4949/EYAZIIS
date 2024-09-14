from beanie import Document


class TextDocument(Document):
    name: str
    text: str

    class Settings:
        name = "text-document"
