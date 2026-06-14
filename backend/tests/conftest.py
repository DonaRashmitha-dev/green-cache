"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def sample_queries():
    return {
        "english": "What is the capital of France?",
        "paraphrase_en": "Tell me France's capital city",
        "telugu": "ఫ్రాన్స్ రాజధాని ఏమిటి?",
        "hindi": "फ्रांस की राजधानी क्या है?",
    }
