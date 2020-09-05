import logging
import sys
import webbrowser
from os import path
from typing import Dict, Set

from GPRMon.github import PRChecks

from PySide2 import QtGui, QtWidgets

BASE_DIR, _ = path.split(path.realpath(__file__))

logger = logging.getLogger('gprmon')


class Resources():
    ACTIVE_ICON = path.join(BASE_DIR, '../resources/octo16x16r.png')
    ACK_ICON = path.join(BASE_DIR, '../resources/octo16x16y.png')
    INACTIVE_ICON = path.join(BASE_DIR, '../resources/octo16x16.png')


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None, conf: Dict = dict()):
        QtWidgets.QSystemTrayIcon.__init__(self, QtGui.QIcon(Resources.INACTIVE_ICON), parent)
        self.menu = QtWidgets.QMenu(parent)
        self.setToolTip('Github Pull Requests MONitor')
        self.conf = conf
        self.ack_items: Set[str] = set()
        self.update_prs()

    def update_prs(self) -> None:
        logger.info('Checking github...')
        menu_items = PRChecks(self.conf).get_pull_requests()
        self._update_menu(menu_items=menu_items)

    def _update_menu(self, menu_items: Set[str]) -> None:
        self.menu.clear()
        self.ack_items = self.ack_items.difference(self.ack_items.difference(menu_items))
        logger.debug(f'Items in ack: {self.ack_items}')
        logger.debug(f'Items to update: {menu_items}')
        for item in menu_items:
            if item not in self.ack_items:
                sub_menu = self.menu.addMenu(' '.join(item.split("/")[4:]))
                action = sub_menu.addAction('Open')
                action.triggered.connect(lambda f=self._open_browser, item=item:
                                         self._open_browser(item))
                action = sub_menu.addAction('Acknowledge')
                action.triggered.connect(lambda f=self._item_acknowledge,
                                         menu_items=menu_items,
                                         item=item:
                                         self._item_acknowledge(menu_items, item))
                self.setIcon(QtGui.QIcon(Resources.ACTIVE_ICON))
            else:
                sub_menu = self.menu.addMenu(f'{" ".join(item.split("/")[4:])} ✓')
                action = sub_menu.addAction('Open')
                action.triggered.connect(lambda f=self._open_browser, item=item:
                                         self._open_browser(item))

        self.menu.addSeparator()

        exit_item = self.menu.addAction('Exit')
        exit_item.triggered.connect(self._shutdown)
        self.setContextMenu(self.menu)

    def _on_activate(self, menu_items: Set['str']) -> None:
        self._update_menu(menu_items=menu_items)
        if menu_items == self.ack_items:
            logger.debug('Changing icon to all ack')
            self.setIcon(QtGui.QIcon(Resources.ACK_ICON))
        else:
            logger.debug('Changing icon to active')
            self.setIcon(QtGui.QIcon(Resources.ACTIVE_ICON))

    def _open_browser(self, url: str) -> None:
        logger.debug(f'Opening {url} using {webbrowser.get().basename}')
        webbrowser.open(url)

    def _item_acknowledge(self, items: Set['str'], item: str) -> None:
        logger.debug(f'Item {item} marked as acknowledge')
        self.ack_items.add(item)
        self._on_activate(items)

    def _shutdown(self) -> None:
        logger.info('Shutting down...')
        sys.exit()
