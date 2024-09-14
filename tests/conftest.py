import pytest

from app.container import ApplicationContainer


@pytest.fixture(scope="session")
def app_container():
    container = ApplicationContainer()

    return container
