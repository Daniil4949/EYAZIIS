import copy
import os
from dataclasses import dataclass

import joblib
import numpy as np
from fastapi import File, HTTPException
from keras.api.layers import Dense
from keras.api.models import Sequential, load_model
from sklearn.feature_extraction.text import CountVectorizer

from app.service.html_processing import HtmlProcessingService
from app.service.language_detection.report_generation.service import (
    ReportGenerationService,
)
from app.service.s3_service import S3Service
from app.service.text_document import TextDocument, TextDocumentService
from app.service.text_document.enums import Language
from app.util.enums import Mode


@dataclass
class NgrammAndNeuralMethodService:
    """
    Service for processing texts and predicting
    language using a neural network.
    """

    mode: str
    html_processing_service: HtmlProcessingService
    text_document_service: TextDocumentService
    s3_service: S3Service
    report_generation_service: ReportGenerationService
    vectorizer: CountVectorizer = None  # Инициализируем векторизатор как None

    @property
    def model_path(self):
        model_path = os.path.join(
            os.path.dirname(__file__),
            (self.mode + "_ru_de_language_model.keras"),
        )
        return model_path

    async def _create_language_labels(self):
        """Creates labels for languages based on texts from the repository."""
        corpus_russian = (
            await self.text_document_service.get_documents_by_language(
                language=Language.RUSSIAN
            )
        )
        corpus_german = (
            await self.text_document_service.get_documents_by_language(
                language=Language.GERMAN
            )
        )

        self.labels_russian = [0] * len(
            corpus_russian
        )  # Labels for Russian language
        self.labels_german = [1] * len(
            corpus_german
        )  # Labels for German language
        self.corpus = corpus_russian + corpus_german  # Combining corpora
        self.labels = (
            self.labels_russian + self.labels_german
        )  # Combining labels

    async def _creating_vectors(self):
        """Creates vectors for texts using the fitted vectorizer."""
        if self.vectorizer is None:
            # Инициализируем векторизатор только один раз
            self.vectorizer = (
                CountVectorizer(analyzer="char", ngram_range=(3, 3))
                if self.mode == Mode.NGRAMM
                else CountVectorizer(analyzer="word")
            )
        self.X = self.vectorizer.fit_transform(
            self.corpus
        )  # Обучаем векторизатор

    async def create_model(self):
        """Creates and trains a neural network for language classification."""
        await self._create_language_labels()
        await self._creating_vectors()

        model = Sequential()
        model.add(
            Dense(64, input_dim=self.X.shape[1], activation="relu")
        )  # First hidden layer
        model.add(Dense(32, activation="relu"))  # Second hidden layer
        model.add(Dense(1, activation="sigmoid"))  # Output layer

        model.compile(
            loss="binary_crossentropy", optimizer="adam", metrics=["accuracy"]
        )  # Compiling the model

        y = np.array(self.labels)  # Converting labels to numpy array
        model.fit(
            self.X.toarray(), y, epochs=10, batch_size=32
        )  # Training the model
        model.save(self.model_path)  # Saving the trained model
        joblib.dump(
            self.vectorizer, (self.mode + "_vectorizer.joblib")
        )  # Saving the vectorizer

    @staticmethod
    async def _load_model(path: str):
        """Loads a model from the specified path."""
        try:
            model = load_model(path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        else:
            return model

    @staticmethod
    async def _load_vectorizer(path: str):
        """Loads a vectorizer from the specified path."""
        try:
            vectorizer = joblib.load(path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        else:
            return vectorizer

    async def predict(self, file: File):
        """Predicts the language of the given texts."""
        file_url = await self.s3_service.upload_file(copy.deepcopy(file))
        texts = [await self.html_processing_service.process_file(file)]
        model = await self._load_model(self.model_path)
        vectorizer = await self._load_vectorizer(
            self.mode + "_vectorizer.joblib"
        )
        languages = []
        if model and vectorizer:
            x_new = vectorizer.transform(texts)  # Transforming the input text
            predictions = model.predict(x_new.toarray())  # Making predictions

            for pred in predictions:
                language = (
                    "de" if pred >= 0.5 else "ru"
                )  # Interpreting predictions
                languages.append(language)
            await self.text_document_service.create_document(
                TextDocument(text=texts[0], language=languages[0])
            )

        return await self.report_generation_service.generate_csv_report(
            file_url=file_url, result=languages[0]
        )
