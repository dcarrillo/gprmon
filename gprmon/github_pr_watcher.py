import asyncio
import json
import logging
from typing import Dict, List, Optional, Set

from PySide2.QtCore import QEventLoop, QObject, QThread, QTimer, Signal

import aiohttp

logger = logging.getLogger('gprmon')

GITHUB_URL = 'https://api.github.com'
API_PATH = '/api/v3'
CONN_TIMEOUT = 5
MAX_CONNECTIONS = 4


async def _fetch_url(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        logger.info(f'Requesting asynchronously: {url}')
        async with session.get(url, allow_redirects=False) as response:
            if response.status != 200:
                logger.error(f'Error requesting {url} status code: {response.status}')
                return None

            return await response.text()
    except aiohttp.ClientError as e:
        raise(e)


async def _fetch_all_urls(urls: List['str'], headers: Dict) -> List[str]:
    connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)

    try:
        async with aiohttp.ClientSession(connector=connector,
                                         headers=headers,
                                         conn_timeout=CONN_TIMEOUT) as session:
            text_responses = await asyncio.gather(*[_fetch_url(session, url) for url in urls])

            return text_responses
    except aiohttp.ClientError as e:
        raise(e)


class GPRmonEmitter(QObject):
    activate = Signal(list)
    deactivate = Signal()


class GithubPrWatcher(QThread):
    def __init__(self, *args, **kwargs):
        conf = kwargs['conf']
        kwargs.pop('conf', None)
        QThread.__init__(self, *args, **kwargs)
        self.emitter = GPRmonEmitter()
        self.org = conf['organization']
        self.url = f"{conf['url']}{API_PATH}"
        self.repos = conf['repos']
        self.user = conf['user']
        self.headers = {'Authorization': f"token {conf['token']}",
                        'Accept': f'application/vnd.github.{API_PATH.split("/")[-1]}+json'}
        self.interval = conf['interval']
        self.watcher_timer = self._initialize_timer()

    def run(self):
        self._get_pull_requests()
        self.watcher_timer.start(self.interval * 1000)
        loop = QEventLoop()
        loop.exec_()

    def _initialize_timer(self):
        timer = QTimer()
        timer.moveToThread(self)
        timer.timeout.connect(self._get_pull_requests)

        return timer

    def _get_pull_requests(self):
        pull_requests = List[str]
        items: Set['str'] = set()

        urls = [f'{self.url}/repos/{self.org}/{repo_name}/pulls'
                for repo_name in self.repos]

        try:
            pull_requests = [pr for pr in asyncio.run(_fetch_all_urls(urls, self.headers)) if pr]
        except TypeError:
            pass
        except aiohttp.ClientError as e:
            logger.error(e)
        except Exception as e:
            logger.error(f'Unhandled exception: {e}')

        for pr in pull_requests:
            items.update([pr_url for pr_url in self._get_prs_by_reviewer(pr)])

        if items:
            logger.debug('Sending activating signal...')
            self.emitter.activate.emit(items)
        else:
            logger.debug('Sending deactivating signal...')
            self.emitter.deactivate.emit()

        # self.watcher_timer.stop()
        # self.exit()

    def _get_prs_by_reviewer(self, pull_requests: List[str]) -> Set[str]:
        matchs = []

        for pr in json.loads(pull_requests):  # type: ignore
            for reviewer in pr['requested_reviewers']:
                if reviewer['login'] == self.user:
                    logger.info(f"{reviewer['login']} has a pending pull request: {pr['html_url']}")
                    matchs.append(pr['html_url'])

        return set(matchs)
