from GPRMon.github import PRChecks

import pytest

from tests import Mocks


@pytest.fixture
def pr_check():
    return PRChecks(Mocks.conf)


def test_get_prs_by_reviewer(pr_check):
    prs = [
        {
            "url": "https://api.github.com/repos/octocat/Hello-World/pulls/1347",
            "id": 1,
            "title": "Amazing new feature",
            "body": "Please pull these awesome changes in!",
            "html_url": "https://github.com/octocat/Hello-World/pull/1347",
            "requested_reviewers": [
                {
                    "login": "other_user",
                    "html_url": "https://github.com/other_user"
                }
            ]
        },
        {
            "url": "https://api.github.com/repos/octocat/Hello-World/pulls/1348",
            "id": 2,
            "title": "Amazing new feature 2",
            "body": "Please pull these awesome changes in!",
            "html_url": "https://github.com/octocat/Hello-World/pull/1348",
            "requested_reviewers": [
                {
                    "login": "another_user",
                    "html_url": "https://github.com/another_user"
                }
            ]
        }
    ]

    matchs = pr_check._get_prs_by_reviewer(prs)

    assert 'https://github.com/octocat/Hello-World/pull/1347' in matchs and len(matchs) == 1
