from conftest import self_name
from logging import getLogger, DEBUG


def test_logger_handler(data):
    logger = getLogger("main")
    logger.setLevel(DEBUG)
    # logger.addHandler(StreamHandler())
    logger.addHandler(data.logging_handler)
    logger.debug("1")
    logger.info("2")
    logger.warning("3")
    logger.error("4")
    logger.critical("5")

    assert len(data.log_store.data_recv[self_name]) == 5
    for i in range(5):
        assert data.log_store.data_recv[self_name][i].level == i + 1
        assert data.log_store.data_recv[self_name][i].message == str(i + 1)


def test_logger_io(data):
    print("a\nb", file=data.logging_io)
    assert len(data.log_store.data_recv[self_name]) == 2
    assert data.log_store.data_recv[self_name][0].level == 2
    assert data.log_store.data_recv[self_name][0].message == "a"
    assert data.log_store.data_recv[self_name][1].level == 2
    assert data.log_store.data_recv[self_name][1].message == "b"
