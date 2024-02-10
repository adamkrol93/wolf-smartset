from datetime import datetime

from httpx import AsyncClient, Headers

from wolf_comm import constants
from wolf_comm.constants import TIMESTAMP
from wolf_comm.helpers import bearer_header


async def create_session(session: AsyncClient, token: str):
    data = {
        TIMESTAMP: datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    resp = await session.post(constants.BASE_URL_PORTAL + "/api/portal/CreateSession2",
                              headers=Headers({**bearer_header(token),
                                               **{"Content-Type": "application/json"}}),
                              json=data)

    return resp.json()['BrowserSessionId']
