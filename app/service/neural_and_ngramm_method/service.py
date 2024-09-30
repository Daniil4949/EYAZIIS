import os
from dataclasses import dataclass

import joblib
import numpy as np
from fastapi import HTTPException
from keras.api.layers import Dense
from keras.api.models import Sequential, load_model
from sklearn.feature_extraction.text import CountVectorizer

from app.service.text_document import TextDocumentService
from app.service.text_document.enums import Language
from app.util.enums import Mode


@dataclass
class NgrammAndNeuralMethodService:
    """
    Service for processing texts and predicting
    language using a neural network.
    """

    mode: str
    text_document_service: TextDocumentService
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

    async def predict(self, text: list[str]):
        """Predicts the language of the given texts."""
        model = await self._load_model(self.model_path)
        vectorizer = await self._load_vectorizer(
            self.mode + "_vectorizer.joblib"
        )

        if model and vectorizer:
            x_new = vectorizer.transform(text)  # Transforming the input text
            predictions = model.predict(x_new.toarray())  # Making predictions

            languages = []
            for pred in predictions:
                language = (
                    "German" if pred >= 0.5 else "Russian"
                )  # Interpreting predictions
                languages.append(language)

            return languages

        return "Couldn't predict language"  # Error message if prediction fails
