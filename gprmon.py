#!/usr/bin/env python3

import logging
import sys
from logging.handlers import RotatingFileHandler
from os import getenv, makedirs, path

import GPRMon

from PySide2 import QtWidgets
from PySide2.QtCore import QTimer

import yaml


logger = logging.getLogger('gprmon')
BASEDIR = path.dirname(__file__)

if not path.exists(f'{BASEDIR}/logs'):
    makedirs(f'{BASEDIR}/logs')

handler = RotatingFileHandler(path.join(BASEDIR, 'logs/gprmon.log'), 'a', 1024 * 1024 * 4, 5)
handler.setFormatter(logging.Formatter('-- %(levelname)s -- %(asctime)s %(message)s'))
logger.addHandler(handler)


if __name__ == '__main__':
    conf_file = path.join(BASEDIR, 'gprmon.yml')

    try:
        with open(conf_file, 'r') as config_file:
            conf = yaml.load(config_file, Loader=yaml.SafeLoader)

        try:
            logger.setLevel(conf['log_level'].upper())
        except KeyError:
            logger.setLevel('INFO')

        conf['interval'] = conf['interval'] if 'interval' in conf else 30

        if getenv('GITHUB_TOKEN'):
            conf['token'] = getenv('GITHUB_TOKEN')
        elif 'token' not in conf:
            raise ValueError('Gihub token has to be provided')

    except (IOError, yaml.YAMLError, ValueError) as e:
        logger.error(e)
        print(e)
        sys.exit(1)

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    tray_app = GPRMon.TrayIcon(widget, conf=conf)
    tray_app.show()

    timer = QTimer(widget)
    timer.setInterval(conf['interval'] * 1000)
    timer.timeout.connect(tray_app.update_prs)
    timer.start()

    logger.info('Starting gprmon...')
    sys.exit(app.exec_())
