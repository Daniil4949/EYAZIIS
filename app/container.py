import operator
from typing import Callable

from beanie import init_beanie
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends, FastAPI

from app.service.alphabet_method.service import AlphabetMethodService
from app.service.calculate_weight_coefficient.service import (
    WeightCoefficientService,
)
from app.service.logical_search.service import LogicalSearchService
from app.service.neural_and_ngramm_method.service import (
    NgrammAndNeuralMethodService,
)
from app.service.open_ai_service.service import OpenAIService
from app.service.text_document import (
    TextDocument,
    TextDocumentRepository,
    TextDocumentService,
)
from app.util.enums import Mode

APP_TITLE = "Logical Search Application"

Provider = providers.Provider


class ApplicationContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    beanie_initialization = providers.Resource(
        init_beanie,
        connection_string=config.mongo.url,
        document_models=[TextDocument],
        allow_index_dropping=False,
    )

    text_document_repository: Provider[TextDocumentRepository] = (
        providers.Singleton(
            TextDocumentRepository,
        )
    )

    text_document_service: Provider[TextDocumentService] = providers.Singleton(
        TextDocumentService,
        text_document_repository=text_document_repository,
    )

    weight_coefficient_service: Provider[WeightCoefficientService] = (
        providers.Singleton(
            WeightCoefficientService,
            text_document_service=text_document_service,
        )
    )

    open_ai_service: Provider[OpenAIService] = providers.Singleton(
        OpenAIService,
        open_ai_token=config.open_ai.token,
    )

    logical_search_service: Provider[LogicalSearchService] = (
        providers.Singleton(
            LogicalSearchService,
            text_document_service=text_document_service,
            open_ai_service=open_ai_service,
        )
    )

    neural_method_service: Provider[NgrammAndNeuralMethodService] = (
        providers.Singleton(
            NgrammAndNeuralMethodService,
            mode=Mode.NEURAL,
            text_document_service=text_document_service,
        )
    )

    ngramm_method_service: Provider[NgrammAndNeuralMethodService] = (
        providers.Singleton(
            NgrammAndNeuralMethodService,
            mode=Mode.NGRAMM,
            text_document_service=text_document_service,
        )
    )

    alphabet_method_service: Provider[AlphabetMethodService] = (
        providers.Singleton(
            AlphabetMethodService,
        )
    )

    app: Callable[[], FastAPI] = providers.Singleton(FastAPI, title=APP_TITLE)


def get_dependency(dependency_name: str) -> Depends:
    """
    Вспомогательная функция позволяющая инжектить зависимости

    >>> from dependency_injector.wiring import inject
    >>>
    >>> @inject
    >>> def some_func(service = get_dependency("some_service")):
    >>>     service.some_method()

    См. https://habr.com/ru/post/528634/
    """
    attr = operator.attrgetter(dependency_name)
    return Depends(Provide[attr(ApplicationContainer)])


dynamic = containers.DynamicContainer()
