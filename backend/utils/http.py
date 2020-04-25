from random import choice
import requests
import logging


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"]
MOBILE_USER_AGENTS = []


def fetch(url, headers=None, cookies=None):
    if headers is None:
        user_agent = choice(USER_AGENTS)
        headers = {'User-Agent': user_agent}
    try:
        with requests.get(url, headers=headers, cookies=cookies) as response:
            response.encoding = response.apparent_encoding
            # TODO: refactor, cookies
            return response.content
    except KeyError as e:
        logger.error(e)
    return ""

async def fetch_async(session, url):
    async with session.get(url) as response:
        return await response.text()

logger = logging.getLogger(__name__)