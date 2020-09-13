import GPRMon

from PySide2 import QtWidgets


class Mocks:
    conf = {
        'organization': '',
        'url': '',
        'repos': ['octocat'],
        'user': 'other_user',
        'headers': {},
        'interval': '',
        'token': ''
    }

    ack_items = set(['https://one', 'https://two'])

    def tray_icon(self) -> GPRMon.TrayIcon:
        QtWidgets.QApplication()
        widget = QtWidgets.QWidget()

        return GPRMon.TrayIcon(widget, conf=self.conf)
