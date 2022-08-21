import json
from typing import Optional
from urllib.parse import urljoin

try:
    import aiohttp
except ImportError:
    aiohttp = None

from .core import LiqPayBase


class AsyncLiqPay(LiqPayBase):
    def __init__(
        self,
        public_key: str,
        private_key: str,
        host: Optional[str] = None,
        sandbox: Optional[bool] = False
    ):
        if not aiohttp:
            raise NotImplementedError('aiohttp not found')

        super(AsyncLiqPay, self).__init__(public_key, private_key, host, sandbox)

    async def api(
        self, 
        url: str,
        params: Optional[dict] = None
    ):
        params = self._prepare_params(params or {})

        json_encoded_params = json.dumps(params)
        signature = self._make_signature(json_encoded_params)

        request_url = urljoin(self._host, url)
        request_data = {'data': json_encoded_params, 'signature': signature}
        async with aiohttp.ClientSession() as session:
            async with session.post(request_url, data=request_data) as response:
                return await response.json()
