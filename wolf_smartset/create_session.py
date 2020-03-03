from httpx import AsyncClient, Headers

from wolf_smartset import constants
from wolf_smartset.helpers import bearer_header


async def create_session(session: AsyncClient, token: str):
    resp = await session.post(constants.BASE_URL + "/api/portal/CreateSession",
                              headers=Headers({**bearer_header(token),
                                               **{"Content-Type": "application/json", "Content-Length": "0"}}))

    return resp.text
