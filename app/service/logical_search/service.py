import re
from dataclasses import dataclass

from app.service.open_ai_service import OpenAIService
from app.service.text_document import TextDocument, TextDocumentService


@dataclass
class LogicalSearchService:
    text_document_service: TextDocumentService
    open_ai_service: OpenAIService

    async def _prepare_query(self, query: str) -> str:
        query = await self.open_ai_service.getting_response_from_open_ai(
            f"i will give u a query in natural "
            f"language like 'I want to see "
            f"python and java' u need to "
            f"answer with query with logical operators "
            f"like 'python and java' if i "
            f"will ask smth like 'I dont want to see python, "
            f"give me java', u should answer "
            f"'not python and java' ur answer should "
            f"include only logical query: {query}"
        )
        return query

    async def search(self, query: str) -> list[TextDocument]:
        """
        Производит поиск документов, удовлетворяюших условию
        :param query: Строка с логическими AND, OR, NOT
        :return: Список документов
        """
        query = await self._prepare_query(query)
        documents = await self._load_documents()
        tokens = await self._tokenize(query)
        parsed_expression = await self._parse_expression(tokens)

        return [
            doc
            for doc in documents
            if await self._evaluate_expression(parsed_expression, doc.text)
            is True
        ]

    async def _load_documents(self) -> list[TextDocument]:
        """
        Загрузка документов из MongoDB.
        :return: список документов.
        """
        documents = await self.text_document_service.get_all_documents()
        return documents

    async def _tokenize(self, query: str) -> list[str]:
        """
        Разбивает строку с логическими AND, OR, NOT на токены
        :param query: строка с логическими AND, OR, NOT
        :return: список токенов
        """
        tokens = re.findall(r"\(|\)|\w+|AND|OR|NOT", query.lower())
        return tokens

    async def _parse_expression(
        self, tokens: list[str]
    ) -> tuple[str | tuple[str]]:
        """
        Разбирает список токенов и создает дерево выражений
        с логическими операторами `AND`, `OR`, и `NOT`.

        Пример:
            tokens =
            ['not','football','and','(','basketball','or','volleyball',')']

            Результат:
            ('and', ('not', 'football'), ('or', 'basketball', 'volleyball'))
        :param tokens: Список токенов, содержащий логическое
                выражение в виде строк.
        :return: Дерево логического выражения, где каждый оператор
         и операнд представлен как строка или вложенный список.
        """

        async def parse_primary():
            token = tokens.pop(0)
            if token == "(":
                # Рекурсивно разбираем подвыражение в скобках
                expr = await self._parse_expression(tokens)
                tokens.pop(0)  # Убираем закрывающую скобку ')'
                return expr
            elif token == "not":
                # NOT - унарный оператор, который
                # применяется к следующему выражению
                return "not", await parse_primary()
            else:
                # Обычное слово
                return token

        async def parse_and_or():
            left = await parse_primary()
            while tokens and tokens[0] in ("and", "or"):
                operator = tokens.pop(0)
                right = await parse_primary()
                left = (operator, left, right)
            return left

        return await parse_and_or()

    async def _evaluate_expression(self, expr, document_content: str) -> bool:
        """
        Рекурсивно оценивает логическое выражение для документа.
        :param expr: Дерево логического выражения, результат
                    self._parse_expression
        :param document_content: Текст, к которому будет
                    применяться логическое выражение
        :return: True, если документ подходит под логическое выражение,
                    иначе False
        """
        if isinstance(expr, str):
            # Проверяем, есть ли слово в документе
            return expr.lower() in document_content.lower()

        if isinstance(expr, tuple):
            operator = expr[0]
            if operator == "not":
                # NOT применяем к следующему выражению
                return not await self._evaluate_expression(
                    expr[1], document_content
                )
            elif operator == "and":
                # AND применяется к двум выражениям
                return await self._evaluate_expression(
                    expr[1], document_content
                ) and await self._evaluate_expression(
                    expr[2], document_content
                )
            elif operator == "or":
                # OR применяется к двум выражениям
                return await self._evaluate_expression(
                    expr[1], document_content
                ) or await self._evaluate_expression(expr[2], document_content)
