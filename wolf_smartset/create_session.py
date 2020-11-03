from datetime import datetime

from httpx import AsyncClient, Headers

from wolf_smartset import constants
from wolf_smartset.constants import TIMESTAMP
from wolf_smartset.helpers import bearer_header


async def create_session(session: AsyncClient, token: str):
    data = {
        TIMESTAMP: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    resp = await session.post(constants.BASE_URL + "/api/portal/CreateSession2",
                              headers=Headers({**bearer_header(token),
                                               **{"Content-Type": "application/json"}}),
                              json=data)

    return resp.json()['BrowserSessionId']
