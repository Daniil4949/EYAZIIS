from dataclasses import dataclass

from fastapi import File

from app.service.html_processing import HtmlProcessingService
from app.service.text_document.enums import Language


@dataclass
class AlphabetMethodService:
    """
    Service for processing texts and predicting
    language using an alphabet frequency method.
    """

    html_processing_service: HtmlProcessingService
    alphabet_frequencies: dict = None

    def __post_init__(self):
        # Определяем частотные характеристики
        # букв для русского и немецкого языков
        self.alphabet_frequencies = {
            Language.RUSSIAN: {
                "а": 0.0817,
                "б": 0.0159,
                "в": 0.0453,
                "г": 0.0170,
                "д": 0.0356,
                "е": 0.0843,
                "ё": 0.0020,
                "ж": 0.0054,
                "з": 0.0135,
                "и": 0.0709,
                "й": 0.0150,
                "к": 0.0350,
                "л": 0.0426,
                "м": 0.0294,
                "н": 0.0670,
                "о": 0.1095,
                "п": 0.0271,
                "р": 0.0422,
                "с": 0.0544,
                "т": 0.0657,
                "у": 0.0231,
                "ф": 0.0022,
                "х": 0.0060,
                "ц": 0.0047,
                "ч": 0.0156,
                "ш": 0.0069,
                "щ": 0.0016,
                "ъ": 0.0007,
                "ы": 0.0193,
                "ь": 0.0185,
                "э": 0.0123,
                "ю": 0.0077,
                "я": 0.0202,
            },
            Language.GERMAN: {
                "a": 0.0651,
                "b": 0.0162,
                "c": 0.0295,
                "d": 0.0502,
                "e": 0.1748,
                "f": 0.0195,
                "g": 0.0188,
                "h": 0.0548,
                "i": 0.0635,
                "j": 0.0027,
                "k": 0.0145,
                "l": 0.0349,
                "m": 0.0252,
                "n": 0.0977,
                "o": 0.0222,
                "p": 0.0031,
                "q": 0.0005,
                "r": 0.0599,
                "s": 0.0659,
                "t": 0.0616,
                "u": 0.0401,
                "v": 0.0075,
                "w": 0.0195,
                "x": 0.0003,
                "y": 0.0010,
                "z": 0.0116,
                "ä": 0.0136,
                "ö": 0.0073,
                "ü": 0.0100,
            },
        }

    async def predict(self, file: File):
        """Predicts the language of the given
        text based on alphabet frequency."""
        text = await self.html_processing_service.process_file(file)
        text = text.lower()  # Приводим текст к нижнему регистру
        text_length = len(text)

        # Подсчитываем частоту букв
        letter_counts = {}
        for letter in text:
            if letter.isalpha():  # Проверяем, что это буква
                letter_counts[letter] = letter_counts.get(letter, 0) + 1

        # Вычисляем относительные частоты
        frequencies = {}
        for letter, count in letter_counts.items():
            frequencies[letter] = count / text_length

        # Сравниваем с частотами для каждого языка
        scores = {Language.RUSSIAN: 0, Language.GERMAN: 0}

        for lang, freq_dict in self.alphabet_frequencies.items():
            for letter, expected_freq in freq_dict.items():
                scores[lang] += (
                    frequencies.get(letter, 0) - expected_freq
                ) ** 2

        # Определяем язык с наименьшей ошибкой
        predicted_language = min(scores, key=scores.get)
        return predicted_language
