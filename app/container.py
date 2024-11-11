import operator
from typing import Callable

import aioboto3
from beanie import init_beanie
from dependency_injector import containers, providers
from dependency_injector.wiring import Provide
from fastapi import Depends, FastAPI

from app.service.alphabet_method.service import AlphabetMethodService
from app.service.calculate_weight_coefficient.service import (
    WeightCoefficientService,
)
from app.service.html_processing.service import HtmlProcessingService
from app.service.logical_search.service import LogicalSearchService
from app.service.neural_and_ngramm_method.service import (
    NgrammAndNeuralMethodService,
)
from app.service.open_ai_service.service import OpenAIService
from app.service.report_generation.service import ReportGenerationService
from app.service.s3_service import S3Service
from app.service.speech_synthesis.service import SpeechSynthesisService
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

    boto3_session: Provider[aioboto3.Session] = providers.Singleton(
        aioboto3.Session,
        aws_access_key_id=config.s3.access_key_id.required(),
        aws_secret_access_key=config.s3.access_key_secret.required(),
        region_name=config.s3.region_name.required(),
    )

    s3_client = providers.Factory(
        boto3_session.provided.client.call(),
        service_name="s3",
        aws_access_key_id=config.s3.access_key_id.required(),
        aws_secret_access_key=config.s3.access_key_secret.required(),
        region_name=config.s3.region_name.required(),
        endpoint_url=config.s3.endpoint.required(),
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

    html_processing_service: Provider[HtmlProcessingService] = (
        providers.Resource(HtmlProcessingService)
    )

    s3_service: Provider[S3Service] = providers.Resource(
        S3Service,
        s3_client_factory=s3_client.provider,
        s3_endpoint=config.s3.endpoint,
        s3_bucket=config.s3.bucket,
    )

    report_generation_service: Provider[ReportGenerationService] = (
        providers.Resource(
            ReportGenerationService,
            text_document_service=text_document_service,
        )
    )

    neural_method_service: Provider[NgrammAndNeuralMethodService] = (
        providers.Singleton(
            NgrammAndNeuralMethodService,
            mode=Mode.NEURAL,
            html_processing_service=html_processing_service,
            text_document_service=text_document_service,
            s3_service=s3_service,
            report_generation_service=report_generation_service,
        )
    )

    ngramm_method_service: Provider[NgrammAndNeuralMethodService] = (
        providers.Singleton(
            NgrammAndNeuralMethodService,
            mode=Mode.NGRAMM,
            html_processing_service=html_processing_service,
            text_document_service=text_document_service,
            s3_service=s3_service,
            report_generation_service=report_generation_service,
        )
    )

    alphabet_method_service: Provider[AlphabetMethodService] = (
        providers.Singleton(
            AlphabetMethodService,
            html_processing_service=html_processing_service,
            text_document_service=text_document_service,
            s3_service=s3_service,
            report_generation_service=report_generation_service,
        )
    )

    speech_synthesis_service: Provider[SpeechSynthesisService] = (
        providers.Singleton(SpeechSynthesisService)
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
