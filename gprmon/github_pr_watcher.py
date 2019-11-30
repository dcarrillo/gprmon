import asyncio
import json
import logging
import threading
import webbrowser
from time import sleep
from typing import Dict, List

import aiohttp
import pystray

from gprmon.icon import Icon

logger = logging.getLogger('gprmon')

GITHUB_URL = 'https://api.github.com'
API_PATH = '/api/v3'
CONN_TIMEOUT = 5
MAX_CONNECTIONS = 4


async def _fetch_url(session: aiohttp.ClientSession, url: str) -> str:
    try:
        logger.info(f'Requesting asynchronously: {url}')
        async with session.get(url, allow_redirects=False) as response:
            if response.status != 200:
                logger.error(f'Error requesting {url} status code: {response.status}')
                return None

            return await response.text()
    except aiohttp.ClientError as e:
        raise(e)


async def _fetch_all_urls(urls: List, headers: Dict) -> List[str]:
    connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)

    try:
        async with aiohttp.ClientSession(connector=connector,
                                         headers=headers,
                                         conn_timeout=CONN_TIMEOUT) as session:
            text_responses = await asyncio.gather(*[_fetch_url(session, url) for url in urls])

            return text_responses
    except aiohttp.ClientError as e:
        logger.error(e)


class GithubPrWatcher(object):
    def __init__(self, icon: Icon, conf: Dict):
        try:
            self.interval = conf['interval']
        except KeyError:
            self.interval = 30

        try:
            self.always_visible = bool(conf['always_visible'])
        except KeyError:
            self.always_visible = False

        self.org = conf['organization']
        self.url = f"{conf['url']}{API_PATH}"
        self.repos = conf['repos']
        self.match = conf['match']
        self.headers = {'Authorization': f"token {conf['token']}",
                        'Accept': f'application/vnd.github.{API_PATH.split("/")[-1]}+json'}
        self.icon = icon
        self.first_time = True

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        logger.info('Starting watcher in background')
        thread.start()

    def run(self):
        self.icon.hide()
        exit_item = pystray.MenuItem("Quit", lambda l: self._shutdown())

        while True:
            pull_requests = []
            items = []

            urls = [f'{self.url}/repos/{self.org}/{repo_name}/pulls'
                    for repo_name in self.repos]

            try:
                pull_requests = [pr for pr in asyncio.run(_fetch_all_urls(urls, self.headers)) if pr]
            except TypeError:
                pass
            except Exception as e:
                logger.error(f'Unhandled exception: f{e}')

            for prs in pull_requests:
                for pr_url in self._get_prs_by_reviewer(prs):
                    items.append(pystray.MenuItem(pr_url, lambda l: self._open_browser(pr_url)))

            if not items and not self.always_visible:
                self.icon.deactivate()
                self.icon.hide()
            else:
                if items:
                    self.icon.activate()
                else:
                    self.icon.deactivate()

                self.icon.show()
                self._first_time_pause()

            items.append(exit_item)
            self.icon.build_menu(pystray.Menu(*items))

            sleep(self.interval)

    def _get_prs_by_reviewer(self, pull_requests: List[str]) -> List[str]:
        matchs = []

        for pr in json.loads(pull_requests):
            for reviewer in pr['requested_reviewers']:
                if reviewer['login'] == self.match:
                    logger.info(f"{reviewer['login']} has a pending pull request: {pr['html_url']}")
                    matchs.append(pr['html_url'])

        return matchs

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
