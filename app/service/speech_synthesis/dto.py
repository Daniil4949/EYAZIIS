from typing import Optional

from pydantic import BaseModel


class SpeechSynthesisDto(BaseModel):
    text: str
    rate: int
    volume: float
    language_id: Optional[int] = None
