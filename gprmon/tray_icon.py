import logging
import sys
import webbrowser
from os import path
from typing import Dict, Set

from PySide2 import QtGui, QtWidgets

from gprmon.github_pr_watcher import GithubPrWatcher

my_dir, _ = path.split(path.realpath(__file__))
ACTIVE_ICON = path.join(my_dir, '../resources/octo16x16r.png')
ACK_ICON = path.join(my_dir, '../resources/octo16x16y.png')
INACTIVE_ICON = path.join(my_dir, '../resources/octo16x16.png')

logger = logging.getLogger('gprmon')


class GPRmonTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None, conf: Dict = dict()):
        QtWidgets.QSystemTrayIcon.__init__(self, QtGui.QIcon(INACTIVE_ICON), parent)
        self.menu = QtWidgets.QMenu(parent)
        self.setToolTip('Github Pull Requests MONitor')
        self.conf = conf
        self.watcher_timer = GithubPrWatcher(None, conf=self.conf)
        self._start_timer()
        self.ack_items: Set[str] = set()
        self._update_menu(set())

    def _start_timer(self):
        logger.info('Launch GithubPrWatcher')
        self.watcher_timer.start()
        self.watcher_timer.emitter.activate.connect(self._on_activate)
        self.watcher_timer.emitter.deactivate.connect(self._on_deactivate)

    def _on_activate(self, menu_items: Set['str']):
        self._update_menu(menu_items)
        if menu_items == self.ack_items:
            logger.debug('Changing icon to all ack')
            QtWidgets.QSystemTrayIcon.setIcon(self, QtGui.QIcon(ACK_ICON))
        else:
            logger.debug('Changing icon to active')
            QtWidgets.QSystemTrayIcon.setIcon(self, QtGui.QIcon(ACTIVE_ICON))

    def _on_deactivate(self):
        self._update_menu([])
        logger.debug('Changing icon to inactive')
        QtWidgets.QSystemTrayIcon.setIcon(self, QtGui.QIcon(INACTIVE_ICON))

    def _update_menu(self, menu_items: Set['str']):
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
            else:
                sub_menu = self.menu.addMenu(f'{" ".join(item.split("/")[4:])} ✓')
                action = sub_menu.addAction('Open')
                action.triggered.connect(lambda f=self._open_browser, item=item:
                                         self._open_browser(item))

        self.menu.addSeparator()

        exit_item = self.menu.addAction('Exit')
        exit_item.triggered.connect(self._shutdown)
        self.setContextMenu(self.menu)

    def _open_browser(self, url: str):
        logger.debug(f'Opening {url} using {webbrowser.get().basename}')
        webbrowser.open(url)

    def _item_acknowledge(self, items: Set['str'], item: str):
        logger.debug(f'Item {item} marked as acknowledge')
        self.ack_items.add(item)
        self._on_activate(items)

    def _shutdown(self):
        logger.info('Shutting down...')
        sys.exit()
