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
        return [doc for doc in documents]

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
        Выполняет логический поиск по запросу с поддержкой вложенных условий.
        :param query: строка запроса с использованием логических
         операторов AND, OR, NOT.
        :return: список названий документов, соответствующих запросу.
        """
        query_tokens = self.tokenize(query)
        return await self._evaluate_expression(query_tokens)

    async def _evaluate_expression(self, tokens):
        """
        Оценивает логическое выражение с поддержкой вложенных условий.
        :param tokens: список токенов выражения.
        :return: множество названий документов, соответствующих выражению.
        """
        operators = {"and", "or", "not"}
        precedence = {"not": 3, "and": 2, "or": 1}
        output = []
        ops_stack = []

        def apply_operator(op):  # noqa
            if op == "not":
                set1 = output.pop()
                result = self._not_operation(set1, set())
            else:
                set2 = output.pop()
                set1 = output.pop()
                if op == "and":
                    result = self._and_operation(set1, set2)
                elif op == "or":
                    result = self._or_operation(set1, set2)
            output.append(result)

        i = 0
        while i < len(tokens):
            token = tokens[i]

            if token == "(":
                ops_stack.append(token)
            elif token == ")":
                while ops_stack and ops_stack[-1] != "(":
                    apply_operator(ops_stack.pop())
                ops_stack.pop()
            elif token in operators:
                while (
                    ops_stack
                    and ops_stack[-1] in operators
                    and precedence[ops_stack[-1]] >= precedence[token]
                ):
                    apply_operator(ops_stack.pop())
                ops_stack.append(token)
            else:
                term_results = await self._find_documents(token)
                output.append(term_results)
            i += 1

        while ops_stack:
            apply_operator(ops_stack.pop())

        return output[0] if output else set()

    async def _find_documents(self, term):
        """
        Ищет документы, содержащие определённый терм.
        :param term: строка с термином.
        :return: множество названий документов, содержащих терм.
        """
        documents = await self.text_document_service.get_all_documents()
        return {
            doc.name for doc in documents if term in self.tokenize(doc.text)
        }

    @staticmethod
    def _and_operation(set1: set[str], set2: set[str]) -> set[str]:
        """
        Реализация логической операции AND.
        :param set1: множество названий документов.
        :param set2: множество названий документов.
        :return: пересечение множеств.
        """
        return set1.intersection(set2)

    @staticmethod
    def _or_operation(set1: set[str], set2: set[str]) -> set[str]:
        """
        Реализация логической операции OR.
        :param set1: множество названий документов.
        :param set2: множество названий документов.
        :return: объединение множеств.
        """
        return set1.union(set2)

    @staticmethod
    def _not_operation(set1: set[str], set2: set[str]) -> set[str]:
        """
        Реализация логической операции NOT.
        :param set1: множество названий документов.
        :param set2: множество названий документов.
        :return: множество документов, которые есть в set1, но не в set2.
        """
        return set1.difference(set2)
