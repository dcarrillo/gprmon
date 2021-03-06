import logging
import pickle
import sys
import webbrowser
from pathlib import Path
from typing import Dict, Set

from GPRMon.github import PRChecks

from PySide2 import QtGui, QtWidgets

BASEDIR = Path(__file__).resolve().parent

logger = logging.getLogger('gprmon')


class Resources():
    ACTIVE_ICON = str(BASEDIR.parent / 'resources/octo16x16r.png')
    ACK_ICON = str(BASEDIR.parent / 'resources/octo16x16y.png')
    INACTIVE_ICON = str(BASEDIR.parent / 'resources/octo16x16.png')


class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None, conf: Dict = dict()):
        QtWidgets.QSystemTrayIcon.__init__(self, QtGui.QIcon(Resources.INACTIVE_ICON), parent)
        self.menu = QtWidgets.QMenu(parent)
        self.setToolTip('Github Pull Requests MONitor')
        self.conf = conf
        self.ack_items: Set[str] = self._load_ack_items()
        self.update_prs()

    def update_prs(self) -> None:
        logger.info('Checking github...')
        menu_items = PRChecks(self.conf).get_pull_requests()
        self._update_menu(menu_items=menu_items)

    def _update_menu(self, menu_items: Set[str]) -> None:
        self.menu.clear()
        self.ack_items = self.ack_items.difference(self.ack_items.difference(menu_items))
        self._save_ack_items()

        logger.debug(f'Items in ack: {self.ack_items}')
        logger.debug(f'Items to update: {menu_items}')

        icon = QtGui.QIcon(Resources.INACTIVE_ICON)
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
                icon = QtGui.QIcon(Resources.ACTIVE_ICON)
            else:
                sub_menu = self.menu.addMenu(f'{" ".join(item.split("/")[4:])} ✓')
                action = sub_menu.addAction('Open')
                action.triggered.connect(lambda f=self._open_browser, item=item:
                                         self._open_browser(item))
                if icon != QtGui.QIcon(Resources.ACTIVE_ICON):
                    icon = QtGui.QIcon(Resources.ACK_ICON)

        self.menu.addSeparator()

        exit_item = self.menu.addAction('Exit')
        exit_item.triggered.connect(self._shutdown)
        self.setIcon(icon)
        self.setContextMenu(self.menu)

    def _save_ack_items(self) -> None:
        logger.debug('Dumping ack items to disk...')
        Path(BASEDIR.parent / '.ack_items').write_bytes(pickle.dumps(self.ack_items))

    def _load_ack_items(self) -> Set[str]:
        logger.debug('Loading ack items from disk...')
        try:
            return pickle.loads(Path(BASEDIR.parent / '.ack_items').read_bytes())
        except FileNotFoundError:
            return set()

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
        self._save_ack_items()
        logger.info('Shutting down...')
        sys.exit()
