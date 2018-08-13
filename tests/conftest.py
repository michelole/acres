import pytest

from acres.preprocess import resource_factory


@pytest.fixture(scope="session", autouse=True)
def path_resource_factory():
    resource_factory.PICKLE_FOLDER = "tests/" + resource_factory.PICKLE_FOLDER
    resource_factory.NGRAMS_FOLDER = "tests/" + resource_factory.NGRAMS_FOLDER
    resource_factory.LOG_FOLDER = "tests/" + resource_factory.LOG_FOLDER
    resource_factory.NN_MODELS_FOLDER = "tests/" + resource_factory.NN_MODELS_FOLDER
