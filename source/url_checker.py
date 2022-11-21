import argparse
import asyncio
import json
from http import HTTPStatus
from typing import Dict, Optional, Sequence, Set, Tuple

import aiohttp
import validators


HTTP_METHODS = [
    'GET', 'HEAD', 'OPTIONS', 'POST', 'PUT',
    'PATCH', 'DELETE', 'CONNECT', 'TRACE',
]
NOT_URL = 'Строка %s не является ссылкой.'
NOT_AVAILABLE_METHODS = 'Ссылка %s не имеет доступных методов.'


def parse_args(data: Optional[Sequence[str]] = None) -> Set[str]:
    """Parse list of urls from command line."""
    description = (
            'Checks the list of passed strings and if the string is a url '
            'it gives the available methods and responses.'
        )
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        'data', nargs='+', default=[], help='List of strings to check'
    )
    args = parser.parse_args(data)

    return set(args.data)


async def validate(data: Set[str]) -> Dict[str, Dict[str, int] | str]:
    """Checks the input strings and returns the verified information."""
    checked_data = {}

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in data:
            if url.startswith('http') and validators.url(url):
                tasks.append(asyncio.ensure_future(get_data(session, url)))
            else:
                checked_data[url] = NOT_URL % url

        additional_data = await asyncio.gather(*tasks)

    return checked_data | dict(additional_data)


async def get_data(
        session: aiohttp.ClientSession,
        url: str
) -> Tuple[str, Dict[str, int] | str]:
    """Checks the existing methods at the url"""
    tasks = []
    for method in HTTP_METHODS:
        tasks.append(asyncio.ensure_future(session.request(method, url)))

    responses = await asyncio.gather(*tasks)
    available_methods = {}
    for response in responses:
        if response.status != HTTPStatus.METHOD_NOT_ALLOWED:
            available_methods[response.method] = response.status

    return url, available_methods or NOT_AVAILABLE_METHODS % url


async def main():
    data = parse_args()
    validation_data = await validate(data)
    print(json.dumps(validation_data, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
