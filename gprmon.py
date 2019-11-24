#!/usr/bin/env python3

import logging
import sys
from logging.handlers import RotatingFileHandler
from os import getenv, path, makedirs

import pystray
import yaml
from PIL import Image

from gprmon.github_pr_watcher import GithubPrWatcher


logger = logging.getLogger('gprmon')
my_dir, _ = path.split(path.realpath(__file__))

if not path.exists(f'{my_dir}/logs'):
    makedirs(f'{my_dir}/logs')

handler = RotatingFileHandler(my_dir + '/logs/gprmon.log', 'a', 1024 * 1024, 4)
handler.setFormatter(logging.Formatter('-- %(levelname)s -- %(asctime)s %(message)s'))
logger.addHandler(handler)

if __name__ == '__main__':
    conf_file = path.join(my_dir, 'gprmon.yml')

    try:
        with open(conf_file, 'r') as config_file:
            conf = yaml.load(config_file, Loader=yaml.SafeLoader)

        try:
            logger.setLevel(conf['log_level'])
        except KeyError:
            logger.setLevel('INFO')

        try:
            if getenv('GITHUB_TOKEN'):
                conf['token'] = getenv('GITHUB_TOKEN')
            else:
                conf['token']
        except KeyError:
            logger.error('Token has to be provided')
            sys.exit(1)
    except (IOError, yaml.YAMLError) as e:
        logger.error(f'Error reading config file {conf_file}:\nf{e}')
        sys.exit(1)

    icon = pystray.Icon('gprmon')
    icon.icon = Image.open(f'{my_dir}/resources/octo16x16.png')
    logger.info('Running systray icon')
    icon.run(lambda l: GithubPrWatcher(icon, conf))
