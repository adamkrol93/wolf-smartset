import datetime
import logging

from httpx import AsyncClient

from wolf_comm import constants

from lxml import html
import pkce
import shortuuid



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
        try:
            # Generate client-sided variables for OpenID
            code_verifier, code_challenge = pkce.generate_pkce_pair()
            state = shortuuid.uuid()
        

            # Retrieve verification token from WOLF website
            r = await session.get(constants.AUTHENTICATION_BASE_URL + '/Account/Login?ReturnUrl=/idsrv/connect/authorize/callback?client_id={}&redirect_uri={}/signin-callback.html&response_type=code&scope=openid%2520profile api role&state={}&code_challenge={}&code_challenge_method=S256&response_mode=query&lang=de-DE'.format(constants.AUTHENTICATION_CLIENT, constants.BASE_URL,state, code_challenge))

            _LOGGER.debug('Verification code response: %s', r.content)

            tree = html.document_fromstring(r.text)
            elements = tree.xpath('//form/input/@value')

            verification_token = elements[0] # __RequestVerificationToken

            # Get code
            login_data = {
                "Input.Username": self.username,
                "Input.Password": self.password,
                "__RequestVerificationToken": verification_token
            }

            r = await session.post(
                constants.AUTHENTICATION_BASE_URL + "/Account/Login",
                params={
                    "ReturnUrl": constants.AUTHENTICATION_URL + "/connect/authorize/callback?client_id={}&redirect_uri={}/signin-callback.html&response_type=code&scope=openid profile api role&state={}&code_challenge={}&code_challenge_method=S256&response_mode=query&lang=de-DE".format(constants.AUTHENTICATION_CLIENT, constants.BASE_URL, state,code_challenge)
                },
                headers={
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                },
                data=login_data,
                cookies = r.cookies,
                follow_redirects=True
            )
            
            _LOGGER.debug('Code response: %s', r.content)
            code = r.url.params['code']
            

            headers = {
                "Cache-control": "no-cache",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:108.0) Gecko/20100101 Firefox/108.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "de-DE,de;q=0.8,en-US;q=0.5,en;q=0.3",
                "Referer": constants.BASE_URL + "/",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            }

            # Get token
            r = await session.post(
                constants.AUTHENTICATION_BASE_URL + "/connect/token",
                headers=headers,
                data={
                    "client_id": "smartset.web",
                    "code": code,
                    "redirect_uri": constants.BASE_URL + "/signin-callback.html",
                    "code_verifier": code_verifier,
                    "grant_type": "authorization_code",
                },
            )
                    
            json = r.json()
            _LOGGER.debug('Token response: %s', json)
            if "error" in json:
                raise InvalidAuth
            return Tokens(json.get("access_token"), json.get("refresh_token"), json.get("expires_in"))
        except:
            raise InvalidAuth

class InvalidAuth(Exception):
    """Please check whether you entered an invalid username or password. If everything looks fine then probably there is an issue with Wolf SmartSet servers."""
    pass
