import asyncio
import logging
from typing import Dict, List, Optional, Set

import aiohttp

import uvloop

logger = logging.getLogger('gprmon')
uvloop.install()

GITHUB_URL = 'https://api.github.com'
API_PATH = '/api/v3'
CONN_TIMEOUT = 5
MAX_CONNECTIONS = 4


async def _fetch_url(session: aiohttp.ClientSession, url: str) -> Optional[Dict]:
    try:
        logger.debug(f'Requesting asynchronously: {url}')
        async with session.get(url, allow_redirects=False) as response:
            if response.status != 200:
                logger.error(f'Error requesting {url} status code: {response.status}')
                return None

            return await response.json()
    except aiohttp.ClientError as e:
        raise(e)


async def _fetch_all_urls(urls: List['str'], headers: Dict = None) -> Dict:
    connector = aiohttp.TCPConnector(limit=MAX_CONNECTIONS)

    try:
        async with aiohttp.ClientSession(connector=connector,
                                         headers=headers,
                                         conn_timeout=CONN_TIMEOUT) as session:
            responses = await asyncio.gather(*[_fetch_url(session, url) for url in urls])

            return responses
    except aiohttp.ClientError as e:
        raise(e)


class PRChecks():
    def __init__(self, conf: Dict = dict()):
        self.org = conf['organization']
        try:
            self.url = f"{conf['url']}{API_PATH}"
        except KeyError:
            self.url = GITHUB_URL

        self.repos = conf['repos']
        self.user = conf['user']
        self.headers = {'Authorization': f"token {conf['token']}",
                        'Accept': f'application/vnd.github.{API_PATH.split("/")[-1]}+json'}
        self.interval = conf['interval']

    def get_pull_requests(self) -> Set['str']:
        pull_requests: List[List] = []
        items: Set['str'] = set()

        urls = [f'{self.url}/repos/{self.org}/{repo_name}/pulls?state=open'
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

        return items

    def _get_prs_by_reviewer(self, pull_requests: List) -> Set[str]:
        matchs: List[str] = []

        for pr in pull_requests:
            logger.debug(f'Found pull request {pr["html_url"]}')
            for reviewer in pr['requested_reviewers']:
                if reviewer['login'] == self.user:
                    logger.info(f'{reviewer["login"]} has a pending pull request: {pr["html_url"]}')
                    matchs.append(pr['html_url'])

        return set(matchs)
