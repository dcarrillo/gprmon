import logging
from os import path

import pystray
from PIL import Image

my_dir, _ = path.split(path.realpath(__file__))
ACTIVE_ICON = path.join(my_dir, '../resources/octo16x16r.png')
INACTIVE_ICON = path.join(my_dir, '../resources/octo16x16.png')

logger = logging.getLogger('gprmon')


class Icon(object):
    def __init__(self, action: object):
        self.icon = pystray.Icon('gprmon')
        self.action = action
        self.icon.icon = Image.open(INACTIVE_ICON)
        self.active = False

    def run(self):
        self.icon.run(self.action)

    def stop(self):
        self.icon.stop()

    def activate(self):
        if not self.active:
            logger.debug('Changing icon to active')
            self.icon.icon = Image.open(ACTIVE_ICON)
            self.active = True

    def deactivate(self):
        if self.active:
            logger.debug('Changing icon to inactive')
            self.icon.icon = Image.open(INACTIVE_ICON)
            self.active = False
