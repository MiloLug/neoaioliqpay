import base64
from copy import deepcopy
import hashlib
import json
from typing import Optional
from urllib.parse import urljoin

class LiqPayBase:
    DEFAULT_API_URL = "https://www.liqpay.ua/api/"

    FORM_TEMPLATE = """\
        <form method="post" action="{action}" accept-charset="utf-8">
        \t{param_inputs}
            <input type="image" src="//static.liqpay.ua/buttons/p1{language}.radius.png" name="btn_text" />
        </form>"""
    INPUT_TEMPLATE = "<input type='hidden' name='{name}' value='{value}'/>"

    SUPPORTED_PARAMS = [
        "public_key", "amount", "currency", "description", "order_id",
        "result_url", "server_url", "type", "signature", "language", "sandbox"
    ]

    def __init__(
        self,
        public_key: str,
        private_key: str,
        host: Optional[str] = None,
        sandbox: Optional[bool] = False
    ):
        self._public_key = public_key
        self._private_key = private_key
        self._host = host or self.DEFAULT_API_URL
        self._sandbox_mode = sandbox

    def _make_signature(self, *args) -> str:
        joined_fields = "".join(x for x in args)
        joined_fields = joined_fields.encode("utf-8")
        return base64.b64encode(hashlib.sha1(joined_fields).digest()).decode("ascii")

    def _prepare_params(self, params: dict) -> dict:
        params = {k: v for k, v in params.items() if k is not None}
        params = {} if params is None else deepcopy(params)
        params.update(public_key=self._public_key)
        return params

    def _encode_params(self, params: dict) -> str:
        params = self._prepare_params(params)
        
        params.update(
            sandbox=int(bool(params.get("sandbox", self._sandbox_mode)))
        )

        encoded_data = self.data_to_sign(params)
        return encoded_data


    async def api(
        self, 
        url: str,
        params: Optional[dict] = None
    ):
        raise NotImplementedError()

    def checkout_url(
        self,
        action: Optional[str],
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        description: Optional[str] = None,
        order_id: Optional[str] = None,
        language: Optional[str] = "ua",
        customer: Optional[str] = None,
        server_url: Optional[str] = None,
        result_url: Optional[str] = None,
        params: Optional[dict] = {},
        **kwargs
    ) -> str:
        """
        This method contains almost same like cnb_form, except we are return just
        url which will helpful for building Restful services.
        :param params:
        :return:
        """
        params.update(kwargs)
        params['action'] = action
        params['amount'] = amount
        params['currency'] = currency
        params['description'] = description
        params['order_id'] = order_id
        params['language'] = language
        params['customer'] = customer
        params['server_url'] = server_url
        params['result_url'] = result_url
        
        
        encoded_data = self._encode_params(params)
        signature = self._make_signature(self._private_key, encoded_data, self._private_key)
        form_action_url = urljoin(self._host, "3/checkout/")

        return f'{form_action_url}?data={encoded_data}&signature={signature}'

    def cnb_form(
        self,
        action: Optional[str],
        amount: Optional[float] = None,
        currency: Optional[str] = None,
        description: Optional[str] = None,
        order_id: Optional[str] = None,
        language: Optional[str] = "ua",
        customer: Optional[str] = None,
        server_url: Optional[str] = None,
        result_url: Optional[str] = None,
        params: Optional[dict] = {},
        **kwargs
    ) -> str:
        
        params.update(kwargs)
        params['action'] = action
        params['amount'] = amount
        params['currency'] = currency
        params['description'] = description
        params['order_id'] = order_id
        params['language'] = language
        params['customer'] = customer
        params['server_url'] = server_url
        params['result_url'] = result_url
        
        encoded_data = self._encode_params(params)
        params_templ = {"data": encoded_data}
        
        params_templ["signature"] = self._make_signature(self._private_key, params_templ["data"], self._private_key)
        form_action_url = urljoin(self._host, "3/checkout/")
        format_input = (lambda k, v: self.INPUT_TEMPLATE.format(name=k, value=v))
        inputs = [format_input(k, v) for k, v in params_templ.items()]
        return self.FORM_TEMPLATE.format(
            action=form_action_url,
            language=language,
            param_inputs="\n\t".join(inputs)
        )

    def cnb_signature(self, params: dict):
        params = self._prepare_params(params)

        data_to_sign = self.data_to_sign(params)
        return self._make_signature(self._private_key, data_to_sign, self._private_key)

    def cnb_data(self, params: dict):
        params = self._prepare_params(params)
        return self.data_to_sign(params)

    def str_to_sign(self, string: str) -> str:
        return base64.b64encode(hashlib.sha1(string.encode("utf-8")).digest()).decode("ascii")

    def data_to_sign(self, params: dict) -> str:
        return base64.b64encode(json.dumps(params).encode("utf-8")).decode("ascii")

    def decode_data_from_str(self, data: str):
        """Decoding data that were encoded by base64.b64encode(str)

        Note:
            Often case of using is decoding data from LiqPay Callback.
            Dict contains all information about payment.
            More info about callback params see in documentation
            https://www.liqpay.ua/documentation/api/callback.

        Args:
            data: json string with api params and encoded by base64.b64encode(str).

        Returns:
            Dict

        Example:
            liqpay = LiqPay(settings.LIQPAY_PUBLIC_KEY, settings.LIQPAY_PRIVATE_KEY)
            data = request.POST.get('data')
            response = liqpay.decode_data_from_str(data)
            print(response)
            {'commission_credit': 0.0, 'order_id': 'order_id_1', 'liqpay_order_id': 'T8SRXWM71509085055293216', ...}

        """
        return json.loads(base64.b64decode(data).decode('utf-8'))
