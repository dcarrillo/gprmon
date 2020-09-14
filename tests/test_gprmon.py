import os
from contextlib import contextmanager
from tempfile import TemporaryDirectory

from tests import Mocks


@contextmanager
def temporary_test_dir():
    oldpwd = os.getcwd()
    with TemporaryDirectory('test/') as td:
        try:
            os.chdir(td)
            yield
        finally:
            os.chdir(oldpwd)


mock_trayicon = Mocks().tray_icon()


@temporary_test_dir()
def test_load_ack_items_file_not_found():
    assert mock_trayicon._load_ack_items() == set()


@temporary_test_dir()
def test_save_and_load_ack_items(mocker):
    mocker.patch.object(mock_trayicon, 'ack_items', Mocks.ack_items)

    mock_trayicon._save_ack_items()

    assert mock_trayicon._load_ack_items() == Mocks.ack_items
