import json
import logging
from typing import List

import requests

GITHUB_URL = 'https://api.github.com'
API_PATH = '/api/v3'

logger = logging.getLogger('gprmon')


class GithubRepo(object):
    def __init__(self, owner: str, repo_name: str, token: str, url: str = GITHUB_URL):
        self.headers = {'Authorization': f'token {token}',
                        'Accept': f'application/vnd.github.{API_PATH.split("/")[-1]}+json'}
        self.owner = owner
        self.repo_name = repo_name
        self.token = token
        self.url = f'{url}{API_PATH}'

    def _get_pull_requests(self) -> List:
        url = f'{self.url}/repos/{self.owner}/{self.repo_name}/pulls'

        try:
            logger.info(f'Requesting {url}')
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code != 200:
                logger.error(f'Error requesting {url} status code: {response.status_code}')

            pull_requests = json.loads(response.text)

            while 'next' in response.links:
                url = response.links['next']['url']
                logger.info(f'Requesting {url}')
                response = requests.get(url, headers=self.headers, timeout=5)
                pull_requests += json.loads(response.text)

        except (requests.RequestException, ValueError) as e:
            logger.error(e)

        return pull_requests

    # TODO implement team match
    def get_prs_by_reviewer(self, match: str, match_type: str = 'user') -> List[int]:
        pull_requests = []

        for pull in self._get_pull_requests():
            if [True for reviewer in pull['requested_reviewers'] if reviewer['login'] == match]:
                pull_requests.append(pull['number'])

        return pull_requests
