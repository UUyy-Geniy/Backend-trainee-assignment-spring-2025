import pytest
from core.config import settings

@pytest.fixture
def postgres_url():
    return str(settings.SQLALCHEMY_TEST_DATABASE_URI)