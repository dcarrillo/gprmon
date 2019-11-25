import logging
import threading
import webbrowser
from os import path
from time import sleep
from typing import Dict

import pystray
import requests
from PIL import Image

from gprmon.github_repo import GithubRepo

logger = logging.getLogger('gprmon')


class GithubPrWatcher(object):
    def __init__(self, icon: pystray.Icon, conf: Dict):
        try:
            self.interval = conf['interval']
        except KeyError:
            self.interval = 30

        try:
            self.always_visible = bool(conf['always_visible'])
        except KeyError:
            self.always_visible = False

        self.org = conf['organization']
        self.url = conf['url']
        self.repos = conf['repos']
        self.match = conf['match']
        self.token = conf['token']
        self.icon = icon
        self.first_time = True

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        logger.info('Starting watcher in background')
        thread.start()

    def run(self):
        self.icon.visible = False
        exit_item = pystray.MenuItem("Exit gprmon", lambda l: self._shutdown())

        while True:
            pull_requests = []
            items = []

            for repo_name in self.repos:
                try:
                    repo = GithubRepo(self.org, repo_name, self.token, self.url)
                    pull_requests = repo.get_prs_by_reviewer(self.match)
                except (requests.RequestException, ValueError) as e:
                    logger.error(e)
                except Exception as e:
                    logger.error(e)

                if pull_requests:
                    for pr in pull_requests:
                        url = f'{self.url}/{self.org}/{repo_name}/pull/{str(pr)}'
                        logger.info(f'PR found: {url}')
                        items.append(pystray.MenuItem(url, lambda l: self._open_browser(url)))

            if not items and not self.always_visible:
                self.icon.visible = False
            else:
                self.icon.visible = True
                self._first_time_pause()

                my_dir, _ = path.split(path.realpath(__file__))

                resource = 'octo16x16r.png' if items else 'octo16x16.png'
                logger.info(f'Changing icon to {resource}')
                self.icon.icon = Image.open(path.join(my_dir, f'../resources/{resource}'))

            items.append(exit_item)
            self.icon.menu = pystray.Menu(*items)

            sleep(self.interval)

    def _open_browser(self, url: str):
        logger.info(f'Opening {url} using {webbrowser.get().basename}')
        webbrowser.open(url)

    def _shutdown(self):
        logger.info('Shutting down...')
        self.icon.stop()

    def _first_time_pause(self):
        if self.first_time:
            sleep(2)
            self.first_time = False
