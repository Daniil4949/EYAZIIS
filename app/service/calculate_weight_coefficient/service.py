import math
import re
from collections import Counter
from dataclasses import dataclass

from app.service.text_document import TextDocumentService


@dataclass
class WeightCoefficientService:
    text_document_service: TextDocumentService

    async def calculate_tfidf(self) -> dict[str, dict[str, float]]:
        """
        Рассчитывает TF-IDF для всех документов.
        :return: словарь {document_name: {term: tf-idf_value}}
        """
        documents = await self.text_document_service.get_all_documents()
        total_docs_count = len(documents)

        term_doc_count = Counter()

        doc_term_frequencies = {}

        for document in documents:
            words = self.tokenize(document.text)
            doc_term_frequencies[document.name] = Counter(words)
            unique_terms = set(words)
            for term in unique_terms:
                term_doc_count[term] += 1

        tfidf_scores = {}

        for document in documents:
            tfidf_scores[document.name] = {}
            word_counts = doc_term_frequencies[document.name]
            for term, count in word_counts.items():
                tf = count
                idf = math.log(total_docs_count / (term_doc_count[term]))
                tfidf_scores[document.name][term] = tf * idf
        return tfidf_scores

    @staticmethod
    def tokenize(text) -> list[str]:
        """
        Преобразует текст в список слов (термов), удаляя знаки препинания.
        :param text: строка текста.
        :return: список термов.
        """
        return re.findall(r"\w+", text.lower())
