import pytest

from app.service.logical_search.service import LogicalSearchService


class TestLogicalSearch:

    @pytest.fixture
    def query(self):
        return "PYTHON OR JAVA"

    @pytest.mark.asyncio
    async def test_search(self, app_container, query):
        service = app_container.logical_search_service()

