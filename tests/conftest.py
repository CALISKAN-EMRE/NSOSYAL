import os
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Set SEMANTIC_MODE=demo for fast, non-download unit test suite
os.environ["SEMANTIC_MODE"] = "demo"

# Ensure backend package is in python path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app, create_app
from app.adapters.json_adapter import JsonDemoAdapter
from app.services.safety_service import SafetyService
from app.services.context_service import ContextService
from app.services.recommendation_service import RecommendationService
from app.services.search_service import SearchService
from app.ml.model_manager import ModelManager


@pytest.fixture(scope="session")
def demo_data_path():
    path = Path(__file__).resolve().parent.parent / "data" / "demo_posts.json"
    assert path.exists(), f"Demo data file must exist at {path}"
    return str(path)


@pytest.fixture(scope="session")
def json_adapter(demo_data_path):
    return JsonDemoAdapter(data_path=demo_data_path)


@pytest.fixture(scope="session")
def safety_service():
    return SafetyService()


@pytest.fixture(scope="session")
def model_manager():
    mm = ModelManager()
    mm.mode = "demo"
    mm._init_demo_services()
    return mm


@pytest.fixture(scope="session")
def context_service(json_adapter, model_manager):
    return ContextService(data_adapter=json_adapter, model_manager=model_manager)


@pytest.fixture(scope="session")
def recommendation_service(json_adapter, safety_service, model_manager):
    return RecommendationService(
        data_adapter=json_adapter, safety_service=safety_service, model_manager=model_manager
    )


@pytest.fixture(scope="session")
def search_service(json_adapter, model_manager):
    return SearchService(data_adapter=json_adapter, model_manager=model_manager)


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
