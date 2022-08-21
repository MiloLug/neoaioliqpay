import json
from typing import Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    requests = None

from .core import LiqPayBase


class LiqPay(LiqPayBase):
    def __init__(
        self,
        public_key: str,
        private_key: str,
        host: Optional[str] = None,
        sandbox: Optional[bool] = False
    ):
        if not requests:
            raise NotImplementedError('requests module not found')

        super(LiqPay, self).__init__(public_key, private_key, host, sandbox)

    def api(
        self, 
        url: str,
        params: Optional[dict] = None
    ):
        params = self._prepare_params(params or {})

        json_encoded_params = json.dumps(params)
        signature = self._make_signature(json_encoded_params)

        request_url = urljoin(self._host, url)
        request_data = {"data": json_encoded_params, "signature": signature}
        with requests.sessions.Session() as session:
            with session.post(request_url, data=request_data) as response:
                return response.json()
