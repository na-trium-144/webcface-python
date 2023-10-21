from pytest import fixture
from webcface.client_data import SyncDataStore2

self_name = "test"


@fixture
def s2():
    return SyncDataStore2[str](self_name)
