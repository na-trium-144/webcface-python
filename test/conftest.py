from pytest import fixture
from webcface.client_data import SyncDataStore2, SyncDataStore1

self_name = "test"


@fixture
def s2():
    return SyncDataStore2[str](self_name)


@fixture
def s1():
    return SyncDataStore1[str](self_name)
