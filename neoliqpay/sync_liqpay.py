import json
from typing import Optional
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    requests = None

from .core import LiqPayBase


class LiqPay(LiqPayBase):
    def __init__(self, *args, **kwargs):
        if not requests:
            raise NotImplementedError('requests module not found')

        super(LiqPay, self).__init__(*args, **kwargs)

    def api(
        self, 
        url: str,
        params: Optional[dict] = None
    ):
        params = self._prepare_params(params or {})

        json_encoded_params = json.dumps(params)
        private_key = self._private_key
        signature = self._make_signature(private_key, json_encoded_params, private_key)

        request_url = urljoin(self._host, url)
        request_data = {"data": json_encoded_params, "signature": signature}
        with requests.sessions.Session() as session:
            with session.post(request_url, data=request_data) as response:
                return response.json()
