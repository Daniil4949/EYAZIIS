# noqa: E501

import io
from dataclasses import dataclass

import nltk
import spacy
from fastapi import Response
from nltk import pos_tag, word_tokenize
from transformers import MarianMTModel, MarianTokenizer

nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("averaged_perceptron_tagger")
nltk.download("averaged_perceptron_tagger_eng")

nlp = spacy.load("en_core_web_sm")


@dataclass
class MachineTranslatorService:
    model_name = "Helsinki-NLP/opus-mt-en-de"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    nlp = spacy.load("en_core_web_sm")
    pos_description = {
        "CC": "Coordinating conjunction",
        # Союз
        "CD": "Cardinal number",
        # Числительное
        "DT": "Determiner",
        # Артикль
        "EX": "Existential there",
        # Экзистенциальный элемент
        "FW": "Foreign word",
        # Иностранное слово
        "IN": "Preposition or subordinating conjunction",
        # Предлог или союз
        "JJ": "Adjective",
        # Прилагательное
        "JJR": "Adjective, comparative",
        # Сравнительное прилагательное
        "JJS": "Adjective, superlative",
        # Превосходное прилагательное
        "NN": "Noun, singular or mass",
        # Существительное
        "NNS": "Noun, plural",
        # Множественное существительное
        "NNP": "Proper noun, singular",
        # Собственное существительное
        "NNPS": "Proper noun, plural",
        # Множественное собственное существительное
        "PDT": "Predeterminer",
        # Предварительный артикль
        "POS": "Possessive ending",
        # Притяжательный суффикс
        "PRP": "Personal pronoun",
        # Личное местоимение
        "PRP$": "Possessive pronoun",
        # Притяжательное местоимение
        "RB": "Adverb",
        # Наречие
        "RBR": "Adverb, comparative",
        # Сравнительное наречие
        "RBS": "Adverb, superlative",
        # Превосходное наречие
        "RP": "Particle",
        # Частица
        "TO": "to",
        # Частица to
        "UH": "Interjection",
        # Восклицание
        "VB": "Verb, base form",
        # Глагол, начальная форма
        "VBD": "Verb, past tense",
        # Глагол, прошедшее время
        "VBG": "Verb, gerund or present participle",
        # Глагол, герундий
        "VBN": "Verb, past participle",
        # Глагол, причастие
        "VBP": "Verb, non-3rd person singular present",
        # Глагол, не 3-е лицо, настоящее время
        "VBZ": "Verb, 3rd person singular present",
        # Глагол, 3-е лицо, настоящее время
        "WDT": "Wh-determiner",
        # Вопросительный артикль
        "WP": "Wh-pronoun",
        # Вопросительное местоимение
        "WP$": "Possessive wh-pronoun",
        # Притяжательное вопросительное местоимение
        "NN|NNS": "Noun or plural noun",
        # Существительное или множественное существительное
    }

    def _translate(self, text):
        inputs = self.tokenizer(text, return_tensors="pt", padding=True)
        translated = self.model.generate(**inputs)
        translated_text = self.tokenizer.batch_decode(
            translated, skip_special_tokens=True
        )
        return translated_text[0]

    @staticmethod
    def _analyze_text(text):
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        return tokens, pos_tags

    @staticmethod
    def _frequency_analysis(tokens):
        freq_dist = nltk.FreqDist(tokens)
        return freq_dist

    @staticmethod
    def _get_parse_tree(doc):
        tree_output = []
        for sent in doc.sents:
            tree_output.append(sent.text + "\n")
            for token in sent:
                tree_output.append(
                    f"{token.text} --> {token.dep_} ({token.head.text})\n"
                )
        return "".join(tree_output)

    def getting_response_file(self, text: str):
        word_count = len(text.split())
        tokens, pos_tags = self._analyze_text(text)
        translated_text = self._translate(text)
        translated_word_count = len(translated_text.split())
        freq_dist = self._frequency_analysis(tokens)

        doc = self.nlp(text)
        parse_tree_output = self._get_parse_tree(doc)

        byte_stream = io.BytesIO()
        byte_stream.write(f"Исходный текст: {text}\n".encode("utf-8"))
        byte_stream.write(
            f"Количество слов во входном тексте: {word_count}\n".encode(
                "utf-8"
            )
        )
        byte_stream.write(
            f"Количество переведённых слов: {translated_word_count}\n".encode(
                "utf-8"
            )
        )
        byte_stream.write(f"Перевод: {translated_text}\n".encode("utf-8"))
        byte_stream.write("Частотный словарь:\n".encode("utf-8"))

        for word, freq in freq_dist.items():
            byte_stream.write(f"{word}: {freq}\n".encode("utf-8"))

        byte_stream.write("Части речи:\n".encode("utf-8"))
        for word, tag in pos_tags:
            byte_stream.write(f"{word}: {tag}\n".encode("utf-8"))

        byte_stream.write("Дерево синтаксического разбора:\n".encode("utf-8"))
        byte_stream.write(
            parse_tree_output.encode("utf-8")
        )  # Добавляем дерево разбора

        byte_stream.seek(0)
        return Response(
            content=byte_stream.getvalue(),
            media_type="application/octet-stream",
            headers={
                "Content-Disposition": "attachment; "
                "filename=translation_results.txt"
            },
        )
