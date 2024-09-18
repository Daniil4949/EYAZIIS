import re
from dataclasses import dataclass

import wikipedia  # Добавляем для работы с Википедией

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

        result_docs = [
            doc
            for doc in documents
            if await self._evaluate_expression(parsed_expression, doc.text)
        ]

        print(f"{result_docs=}", end="\n--------------------------")

        # Если документы не найдены, идем в Википедию
        if not result_docs:
            search_terms = self._get_search_terms(parsed_expression)
            print(f"{search_terms=}")
            if search_terms:
                result_docs = await self._search_in_wikipedia(search_terms)

            print(f"{result_docs=}")

        return result_docs

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
        """

        async def parse_primary():
            token = tokens.pop(0)
            if token == "(":
                expr = await self._parse_expression(tokens)
                tokens.pop(0)  # Убираем закрывающую скобку ')'
                return expr
            elif token == "not":
                return "not", await parse_primary()
            else:
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
        """
        if isinstance(expr, str):
            return expr.lower() in document_content.lower()

        if isinstance(expr, tuple):
            operator = expr[0]
            if operator == "not":
                return not await self._evaluate_expression(
                    expr[1], document_content
                )
            elif operator == "and":
                return await self._evaluate_expression(
                    expr[1], document_content
                ) and await self._evaluate_expression(
                    expr[2], document_content
                )
            elif operator == "or":
                return await self._evaluate_expression(
                    expr[1], document_content
                ) or await self._evaluate_expression(expr[2], document_content)

    def _get_search_terms(self, expr) -> list[str]:
        """
        Извлекает термины для поиска в Википедии из логического выражения.
        :param expr: Дерево логического выражения
        :return: Список терминов для поиска в Википедии
        """
        if isinstance(expr, str):
            return [expr]

        if isinstance(expr, tuple):
            operator = expr[0]
            if operator == "not":
                return []
            elif operator in ("and", "or"):
                left_terms = self._get_search_terms(expr[1])
                right_terms = self._get_search_terms(expr[2])
                return left_terms + right_terms

        return []

    async def _search_in_wikipedia(
        self, search_terms: list[str]
    ) -> list[TextDocument]:
        """
        Выполняет поиск в Википедии по ключевым словам.
        :param search_terms: список ключевых слов для поиска
        :return: список документов с результатами из Википедии
        """
        result_docs = []
        for term in search_terms:
            try:
                # Получаем объект страницы
                page = wikipedia.page(term)
                summary = page.summary[
                    :500
                ]  # Берем первые 500 символов для краткого описания
                url = page.url  # Ссылка на страницу

                # Создаем документ с текстом и URL
                doc = TextDocument(name=term, text=summary, link=url)
                await self.text_document_service.create_document(data=doc)
                result_docs.append(doc)

            except wikipedia.exceptions.DisambiguationError as e:
                # Если много значений, возьмем первое
                page = wikipedia.page(e.options[0])
                summary = page.summary[:500]
                url = page.url

                doc = TextDocument(name=term, text=summary, link=url)
                await self.text_document_service.create_document(data=doc)

                result_docs.append(doc)

            except wikipedia.exceptions.PageError:
                # Если страница не найдена
                continue

        return result_docs
