import datetime
import logging

from httpx import AsyncClient

from wolf_smartset import constants

_LOGGER = logging.getLogger(__name__)


class Tokens:
    """Has two tokens: access and refresh"""

    def __init__(self, access_token: str, refresh_token: str, expires_in: int):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expire_date = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)


class TokenAuth:
    """Adds poosibility to login with passed credentials"""

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    async def token(self, session: AsyncClient) -> Tokens:
        data = {
            'grant_type': 'password',
            'username': self.username,
            'password': self.password,
            'scope': 'offline_access openid api'
        }

        resp = await session.post(constants.BASE_URL + "/connect/token2", data=data)
        json = resp.json()
        _LOGGER.debug('Token response: %s', json)
        if "error" in json:
            raise InvalidAuth
        return Tokens(json.get("access_token"), json.get("refresh_token"), json.get("expires_in"))


class InvalidAuth(Exception):
    """Invalid username and password was passed"""
    pass
