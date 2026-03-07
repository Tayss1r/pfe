# tests/conftest.py
# conftest.py prépare le client de test.
"""
Quand un test utilise client, pytest :

démarre ton application FastAPI en mode test

remplace la vraie session base de données par une fausse session mockée

envoie une requête HTTP à ton API

récupère la réponse

nettoie à la fin

Donc tu testes ton endpoint sans utiliser la vraie base de données.

"""


import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import get_session


@pytest.fixture()
def fastapi_app():
    return app


@pytest.fixture()
def client(fastapi_app):
    async def override_get_session():
        yield AsyncMock(name="AsyncSession")

    fastapi_app.dependency_overrides[get_session] = override_get_session

    with TestClient(fastapi_app) as c:
        yield c

    fastapi_app.dependency_overrides.clear()