from pydantic import BaseModel


class MachineTranslatorRequest(BaseModel):
    text: str
