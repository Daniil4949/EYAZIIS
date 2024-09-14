import re
from dataclasses import dataclass

from app.service.text_document import TextDocumentService


@dataclass
class LogicalSearchService:
    text_document_service: TextDocumentService

    async def _load_documents(self):
        """
        Загрузка документов из MongoDB.
        :return: список текстов документов.
        """
        documents = await self.text_document_service.get_all_documents()
        return [doc.text for doc in documents]

    @staticmethod
    def tokenize(text):
        """
        Преобразует текст в список слов (термов), удаляя знаки препинания.
        :param text: строка текста.
        :return: список термов.
        """
        return re.findall(r"\w+", text.lower())

    async def search(self, query):
        """
        Выполняет логический поиск по запросу.
        :param query: строка запроса с использованием
        логических операторов AND, OR, NOT.
        :return: список индексов документов, соответствующих запросу.
        """
        # Разделение запроса на части по операторам
        query_tokens = self.tokenize(query)
        results = None

        i = 0
        while i < len(query_tokens):
            token = query_tokens[i]

            if token == "and":
                i += 1
                token_next = query_tokens[i]
                results = self._and_operation(
                    results, await self._find_documents(token_next)
                )
            elif token == "or":
                i += 1
                token_next = query_tokens[i]
                results = self._or_operation(
                    results, await self._find_documents(token_next)
                )
            elif token == "not":
                i += 1
                token_next = query_tokens[i]
                results = self._not_operation(
                    results, await self._find_documents(token_next)
                )
            else:
                if results is None:
                    results = await self._find_documents(token)
                else:
                    results = self._and_operation(
                        results, await self._find_documents(token)
                    )
            i += 1

        return results if results is not None else []

    async def _find_documents(self, term):
        """
        Ищет документы, содержащие определённый терм.
        :param term: строка с термином.
        :return: множество индексов документов, содержащих терм.
        """
        documents = await self.text_document_service.get_all_documents()
        return {
            i
            for i, doc in enumerate(documents)
            if term in self.tokenize(doc.text)
        }

    @staticmethod
    def _and_operation(first_set, second_set):
        """
        Реализация логической операции AND.
        :param first_set: множество индексов документов.
        :param second_set: множество индексов документов.
        :return: пересечение множеств.
        """
        if first_set is None:
            return second_set
        return first_set.intersection(second_set)

    @staticmethod
    def _or_operation(first_set, second_set):
        """
        Реализация логической операции OR.
        :param first_set: множество индексов документов.
        :param second_set: множество индексов документов.
        :return: объединение множеств.
        """
        if first_set is None:
            return second_set
        return first_set.union(second_set)

    async def _not_operation(self, first_set, second_set):
        """
        Реализация логической операции NOT.
        :param first_set: множество индексов документов.
        :param second_set: множество индексов документов.
        :return: множество документов, которые есть в set1, но не в set2.
        """
        documents = await self._load_documents()
        if first_set is None:
            return set(range(len(documents))).difference(second_set)
        return first_set.difference(second_set)
