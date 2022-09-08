"""
Miner Dashboard
API
"""

import requests


class API:
    """
    Abstract API class
    """
    def __init__(self, api_key: str = None):
        self._api_key: str = api_key
        self._url = None

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, new_api_key: str):
        self._api_key = new_api_key

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, new_url: str):
        self._url = new_url

    def get_data(self) -> dict | None:
        raise NotImplementedError


class SlushAPI(API):
    """
    Slushpool API class
    """
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        self.url = 'https://slushpool.com/accounts/profile/json/btc/'

    def get_data(self) -> dict | None:
        """
        Get and parse data from Slushpool (BraiinsPool) API
        """
        if not self.api_key:
            return None

        try:
            req = requests.get(self.url, headers={"SlushPool-Auth-Token": self.api_key})
        except requests.exceptions.RequestException:
            return None

        if req.status_code == requests.codes.ok:
            try:
                result = req.json()
                return result['btc']
            except (requests.exceptions.JSONDecodeError, KeyError):
                return None


class BlockchainAPI(API):
    """
    Blockchain.info API class
    """
    TICKERS_URL = 'https://blockchain.info/ticker'

    def __init__(self, address: str):
        super().__init__()
        self.address = address
        self.url = 'https://blockchain.info/balance?active='

    def get_btc_price(self) -> float | None:
        """
        Get last USD/BTC market price
        """
        try:
            req = requests.get(self.TICKERS_URL)
        except requests.exceptions.RequestException:
            return None

        if req.status_code == requests.codes.ok:
            try:
                result = req.json()
                return result['USD']['last']
            except (requests.exceptions.JSONDecodeError, KeyError):
                return None

    def get_address_info(self) -> float | None:
        """
        Get current BTC address balance
        """

        try:
            req = requests.get(self.url + self.address)
        except requests.exceptions.RequestException:
            return None

        if req.status_code == requests.codes.ok:
            try:
                result = req.json()
                return round(result[self.address]['final_balance'] / 1e8, 8)
            except (requests.exceptions.JSONDecodeError, KeyError):
                return None

    def get_data(self) -> dict | None:
        """
        Returns dict with BTC and computed USD balance
        """
        if not self.address:
            return None

        btc_balance = self.get_address_info()
        price = self.get_btc_price()

        if btc_balance and price:
            usd_balance = btc_balance * price

            return {'btc_balance': btc_balance,
                    'usd_balance': usd_balance,
                    'btc_usd_price': price}

        return None


class AltFNG(API):
    """
    Alternative.me Fear and Greed API class
    """
    def __init__(self):
        super().__init__()
        self.url = 'https://api.alternative.me/fng/'

    @staticmethod
    def compute_fng(value: int) -> dict:
        if value < 33:
            color = '#d32f2fe0'
            icon = 'gauge-empty'
        elif value <= 66:
            color = '#f57c00e0'
            icon = 'gauge-low'
        else:
            color = '#afb42be0'
            icon = 'gauge'

        return {'color': color, 'icon': icon}

    def get_data(self) -> dict | None:

        try:
            req = requests.get(self.url)
        except requests.exceptions.RequestException:
            return None

        if req.status_code == requests.codes.ok:
            try:
                result = req.json()['data'][0]['value']
                return self.compute_fng(int(result))
            except (requests.exceptions.JSONDecodeError, KeyError):
                return None
