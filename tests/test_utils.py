import json
from typing import Any

import GPRMon.github as gb

from aiohttp import web

import uvloop


MOCK_PORT = 9999
uvloop.install()


async def _get_url(request: web.Request) -> web.Response:
    response_body = [
        {
            'url': str(request.url),
            'id': 1
        }
    ]

    return web.Response(
        body=json.dumps(response_body),
        content_type='application/json'
    )


async def test_fetch_all_urls(aiohttp_server: Any) -> None:
    app = web.Application()
    app.add_routes([
        web.get(r'/repos/octocat/{name:.+}/pulls', _get_url)
    ])
    await aiohttp_server(app, port=MOCK_PORT)

    urls = [
        f'http://localhost:{MOCK_PORT}/repos/octocat/hello/pulls',
        f'http://localhost:{MOCK_PORT}/repos/octocat/foo/pulls',
        f'http://localhost:{MOCK_PORT}/repos/octocat/var/pulls'
    ]

    responses = await gb._fetch_all_urls(urls)

    assert len(responses) == len(urls)
