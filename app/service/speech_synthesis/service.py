from dataclasses import dataclass

import pyttsx3

from app.service.speech_synthesis.dto import SpeechSynthesisDto


@dataclass
class SpeechSynthesisService:

    @staticmethod
    def pronounce_text(data: SpeechSynthesisDto):
        engine = pyttsx3.init()
        engine.setProperty("rate", data.rate)
        engine.setProperty("volume", data.volume)
        voices = engine.getProperty("voices")
        if data.language_id:
            engine.setProperty("voice", voices[data.language_id].id)
        engine.say(data.text)
        engine.runAndWait()
