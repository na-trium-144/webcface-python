from conftest import self_name
from logging import getLogger, DEBUG
from webcface.log_handler import Handler, LogWriteIO

def test_logger_handler(data):
    logger = getLogger("main")
    logger.setLevel(DEBUG)
    # logger.addHandler(StreamHandler())
    logger.addHandler(Handler(data, "b"))
    logger.debug("1")
    logger.info("2")
    logger.warning("3")
    logger.error("4")
    logger.critical("5")

    assert len(data.log_store.data_recv[self_name]["b"].data) == 5
    for i in range(5):
        assert data.log_store.data_recv[self_name]["b"].data[i].level == i + 1
        assert data.log_store.data_recv[self_name]["b"].data[i].message == str(i + 1)


def test_logger_io(data):
    print("a\nb", file=LogWriteIO(data, "b"))
    assert len(data.log_store.data_recv[self_name]["b"].data) == 2
    assert data.log_store.data_recv[self_name]["b"].data[0].level == 2
    assert data.log_store.data_recv[self_name]["b"].data[0].message == "a"
    assert data.log_store.data_recv[self_name]["b"].data[1].level == 2
    assert data.log_store.data_recv[self_name]["b"].data[1].message == "b"
