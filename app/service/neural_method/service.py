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


@dataclass
class NeuralMethodService:
    """
    Service for processing texts and
    predicting language using a neural network.
    """

    text_document_service: TextDocumentService
    vectorizer = CountVectorizer(analyzer="char", ngram_range=(3, 3))
    model_path = os.path.join(
        os.path.dirname(__file__), "ru_de_language_model.keras"
    )

    async def _create_language_labels(self):
        """Creates labels for languages based on texts from the repository.

        Retrieves texts in Russian and German, assigning labels:
        0 for Russian and 1 for German.
        """
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
        )  # Labels for the Russian language
        self.labels_german = [1] * len(
            corpus_german
        )  # Labels for the German language
        self.corpus = corpus_russian + corpus_german  # Combining corpora
        self.labels = (
            self.labels_russian + self.labels_german
        )  # Combining labels

    async def _creating_vectors(self):
        """Creates vectors for texts using the fitted vectorizer."""
        self.X = self.vectorizer.fit_transform(self.corpus)

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
            self.vectorizer, "vectorizer.joblib"
        )  # Saving the vectorizer

    @staticmethod
    async def _load_model(path: str):
        """Loads a model from the specified path.

        Raises an HTTPException if the model cannot be loaded.
        """
        try:
            model = load_model(path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        else:
            return model

    @staticmethod
    async def _load_vectorizer(path: str):
        """Loads a vectorizer from the specified path.

        Raises an HTTPException if the vectorizer cannot be loaded.
        """
        try:
            vectorizer = joblib.load(path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
        else:
            return vectorizer

    async def predict(self, text: list[str]):
        """Predicts the language of the given texts.

        Loads the trained model and vectorizer, transforms the input text,
        and returns the predicted languages.
        """
        model = await self._load_model(self.model_path)
        vectorizer = await self._load_vectorizer("vectorizer.joblib")

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
