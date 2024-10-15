import re
from collections import Counter, defaultdict
from dataclasses import dataclass

import nltk
import numpy as np
import spacy
from docx import Document
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

from app.service.language_detection.alphabet_method import (
    AlphabetMethodService,
)

nltk.download('punkt')
nltk.download('stopwords')


@dataclass
class ReferatService:
    """
    Сервис для генерации классического реферата и извлечения ключевых слов из текста.
    """
    language_prediction_service: AlphabetMethodService

    async def keyword(self, text: str, top_n: int = 100) -> str:
        """
        Извлекает ключевые слова из текста и строит иерархию по ним.

        :param text: Исходный текст для обработки.
        :param top_n: Максимальное количество ключевых слов для извлечения.
        :return: Иерархия ключевых слов в виде словаря.
        """
        language = await self.language_prediction_service._predict_language(text)
        nlp = spacy.load(f"{language.value}_core_news_sm")
        keywords = await self._extract_keywords(nlp, text, top_n)
        hierarchy = await self._build_hierarchy(keywords)
        return await self._generate_report(hierarchy)

    @staticmethod
    async def _extract_keywords(nlp, document, top_n):
        """
        Извлекает ключевые фразы (существительные, имена собственные, прилагательные) из документа.

        :param nlp: Загруженная модель spaCy для определенного языка.
        :param document: Текст документа для анализа.
        :param top_n: Максимальное количество ключевых фраз для извлечения.
        :return: Список топ ключевых фраз.
        """
        doc = nlp(document)
        noun_phrases = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN', 'ADJ']:
                phrase = ''
                for child in token.children:
                    if child.pos_ in ['NOUN', 'PROPN', 'ADJ']:
                        phrase += child.lemma_ + ' '
                phrase += token.lemma_
                noun_phrases.append(phrase.lower())

        freq = defaultdict(int)
        for phrase in noun_phrases:
            freq[phrase] += 1

        sorted_phrases = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        top_phrases = [phrase for phrase, count in sorted_phrases][:top_n]

        return top_phrases

    @staticmethod
    async def _build_hierarchy(keywords):
        """
        Строит иерархию ключевых слов на основе первых слов в фразах.

        :param keywords: Список ключевых слов.
        :return: Иерархия в виде словаря, где ключ — родительское слово, значение — список дочерних фраз.
        """
        hierarchy = defaultdict(list)
        for keyword in keywords:
            words = keyword.split()
            if len(words) > 1:
                parent = words[0]
                child = keyword
                hierarchy[parent].append(child)
        return hierarchy

    @staticmethod
    async def _generate_report(hierarchy):
        """
        Генерирует текстовый отчет на основе иерархии ключевых слов.

        :param hierarchy: Иерархия ключевых слов в виде словаря.
        :return: Строка с отчетом.
        """
        report = ''
        for parent_word, child_phrases in hierarchy.items():
            report += f'\n{parent_word}\n'
            for phrase in child_phrases:
                report += f'\t{phrase}\n'
        print(report)
        return report

    async def classic(self, text: str, top_n: int = 10) -> str:
        """
        Генерирует классический реферат на основе исходного текста.

        :param text: Исходный текст для генерации реферата.
        :param top_n: Количество предложений в итоговом реферате.
        :return: Сгенерированный реферат в виде строки.
        """
        language = await self.language_prediction_service._predict_language(text)
        nlp = spacy.load(f"{language.value}_core_news_sm")

        sentences = await self._tokenize_sentences(text)

        word_frequencies, tf_max = await self._compute_word_frequencies(text)

        sentence_weights = await self._compute_sentence_weights(sentences, text, word_frequencies, tf_max)

        abstract = await self._select_top_sentences(sentences, sentence_weights, top_n)

        return abstract

    @staticmethod
    async def _tokenize_sentences(text):
        """
        Разбивает текст на предложения.

        :param text: Исходный текст.
        :return: Список предложений.
        """
        sentences = sent_tokenize(text)
        return sentences

    @staticmethod
    async def _preprocess_word(word, stop_words):
        """
        Предобрабатывает слово: удаляет стоп-слова, числа и слова с латинскими буквами.

        :param word: Слово для предобработки.
        :param stop_words: Множество стоп-слов.
        :return: Предобработанное слово или None, если слово должно быть удалено.
        """
        if word.lower() in stop_words:
            return None
        if re.search('[A-Za-z]', word):  # Слово содержит латинские буквы
            return None
        if re.fullmatch(r'\d+', word):  # Слово является числом
            return None
        return word

    @staticmethod
    async def _compute_word_frequencies(text):
        """
        Вычисляет частоты слов в тексте после предобработки.

        :param text: Исходный текст.
        :return: Кортеж (словарь частот слов, максимальная частота tf_max).
        """
        words = word_tokenize(text)
        stop_words = set(stopwords.words('russian'))
        preprocessed_words = []
        for word in words:
            word = word.lower()
            word = await ReferatService._preprocess_word(word, stop_words)
            if word is not None:
                preprocessed_words.append(word)
        word_frequencies = Counter(preprocessed_words)
        tf_max = max(word_frequencies.values())
        return word_frequencies, tf_max

    @staticmethod
    async def _compute_sentence_weights(sentences, text, word_frequencies, tf_max):
        """
        Вычисляет вес каждого предложения на основе TF-IDF и позиций в документе и абзаце.

        :param sentences: Список предложений.
        :param text: Исходный текст.
        :param word_frequencies: Частоты слов в документе.
        :param tf_max: Максимальная частота слова в документе.
        :return: Список кортежей (предложение, вес).
        """
        sentence_weights = []
        total_chars = len(text)
        char_count_until_sentence = 0

        for sentence in sentences:
            sentence_char_len = len(sentence)
            words = word_tokenize(sentence)
            stop_words = set(stopwords.words('russian'))
            preprocessed_words = []
            for word in words:
                word = word.lower()
                word = await ReferatService._preprocess_word(word, stop_words)
                if word is not None:
                    preprocessed_words.append(word)

            # Вычисление tf(t, Si)
            tf_in_sentence = Counter(preprocessed_words)

            # Вычисление Score(Si)
            score_si = 0
            for t in tf_in_sentence:
                tf_t_si = tf_in_sentence[t]
                tf_t_d = word_frequencies[t]
                w_t_d = 0.5 * (1 + tf_t_d / tf_max)
                # Поскольку у нас только один документ, компонент IDF установлен в 1
                idf_t = 1
                w_t_d *= idf_t
                score_si += tf_t_si * w_t_d

            # Вычисление Posd(Si)
            BD_Si = char_count_until_sentence
            Posd_Si = 1 - (BD_Si / total_chars)

            # Вычисление Posp(Si)
            # Предполагается, что абзацы разделены '\n\n' или '\n'
            paragraphs = re.split(r'\n\n|\n', text)
            char_count = 0
            sentence_in_paragraph = False
            for para in paragraphs:
                para_len = len(para)
                if sentence in para:
                    BP_Si = char_count_until_sentence - char_count
                    P_len = para_len
                    Posp_Si = 1 - (BP_Si / P_len) if P_len > 0 else 1
                    sentence_in_paragraph = True
                    break
                else:
                    char_count += para_len
            if not sentence_in_paragraph:
                Posp_Si = 1

            # Вычисление веса предложения
            weight_si = Posd_Si * Posp_Si * score_si

            sentence_weights.append((sentence, weight_si))

            char_count_until_sentence += sentence_char_len

        return sentence_weights

    @staticmethod
    async def _select_top_sentences(sentences, sentence_weights, top_n):
        """
        Выбирает топ-N предложений с наибольшим весом и сохраняет их исходный порядок.

        :param sentences: Список всех предложений исходного текста.
        :param sentence_weights: Список кортежей (предложение, вес).
        :param top_n: Количество предложений для включения в реферат.
        :return: Итоговый реферат в виде строки.
        """
        # Сортировка предложений по весу
        sentence_weights_sorted = sorted(sentence_weights, key=lambda x: x[1], reverse=True)
        # Выбор топ-N предложений
        top_sentences = [s for s, w in sentence_weights_sorted[:top_n]]
        # Сохранение исходного порядка предложений
        sentence_order = {s: i for i, s in enumerate(sentences)}
        top_sentences_sorted = sorted(top_sentences, key=lambda s: sentence_order[s])
        # Объединение предложений в реферат
        abstract = ' '.join(top_sentences_sorted)
        return abstract


    # @staticmethod
    # async def extract_text_from_docx(file):
    #     document = Document(file)
    #     full_text = []
    #     for para in document.paragraphs:
    #         full_text.append(para.text)
    #     return '\n'.join(full_text)
