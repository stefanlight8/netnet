from aiohttp import ClientSession
from yarl import URL

BASE_URL = URL("https://kawaii.red/api")


def build_url(token: str, endpoint: str) -> str:
    uri = str(URL(BASE_URL / "gif" / endpoint % f"token={token}"))
    print(uri)
    return uri


class KawaiiAPI:
    def __init__(self, token: str, session: ClientSession) -> None:
        self.token = token
        self.session = session

    async def get(self, endpoint: str) -> str:
        async with self.session.request(
            'GET',
            build_url(self.token, endpoint)
        ) as response:
            if response.status in (200, 201):
                response = await response.json()
                return response['response']
            else:
                raise TypeError(f'Something is wrong. <Response {response.status}>')
