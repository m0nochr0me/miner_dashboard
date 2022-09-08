"""
Miner Dashboard
Core
"""

from time import strftime
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ColorProperty
from kivy.clock import Clock
from kivymd.uix.relativelayout import RelativeLayout
from kivymd.app import MDApp

from .api import SlushAPI, BlockchainAPI, AltFNG


class Singleton(type):
    """
    Singleton metaclass
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MinerDashboard(MDApp, metaclass=Singleton):
    """
    Application class
    """

    last_update = StringProperty('')
    # Properties
    slushpool_api_key = StringProperty('')
    btc_addr = StringProperty('')
    slushpool_hashrate = NumericProperty(0)
    slushpool_reward = NumericProperty(0)
    slushpool_reward_confirmed = NumericProperty(0)
    btc_balance = NumericProperty(0)
    usd_btc_balance = NumericProperty(0)
    btc_usd = NumericProperty(0)
    btc_fng_icon = StringProperty('gauge')
    btc_fng_color = ColorProperty('#aebfc4e0')
    btc_ok_workers = NumericProperty(0)
    btc_low_workers = NumericProperty(0)
    btc_off_workers = NumericProperty(0)
    slushpool_spinner = BooleanProperty(False)
    blockchain_spinner = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_cls.material_style = "M3"
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.accent_palette = "Indigo"
        self.theme_cls.theme_style = "Dark"
        self.screen = Builder.load_file('layout.kv')
        self.counter = self.update_interval = 60

        self.slush_api = SlushAPI(api_key='')
        self.blockchain_api = BlockchainAPI(address='')
        self.altfng_api = AltFNG()

    def build_config(self, config):
        config.setdefaults('main', {
            'slushpool_api_key': '',
            'btc_addr': ''
        })

    def save_config(self):
        slushpool_api_key_field = self.screen.ids.in_slushpool_api_key
        self.slushpool_api_key = slushpool_api_key_field.text
        self.config.set('main', 'slushpool_api_key', self.slushpool_api_key)
        self.slush_api.api_key = self.slushpool_api_key

        btc_addr_field = self.root.ids.in_btc_addr
        self.btc_addr = btc_addr_field.text
        self.config.set('main', 'btc_addr', self.btc_addr)
        self.blockchain_api.address = self.btc_addr

        self.config.write()

    def build(self):
        slushpool_api_key_field = self.screen.ids.in_slushpool_api_key
        self.slushpool_api_key = slushpool_api_key_field.text = self.config.get('main', 'slushpool_api_key')
        self.slush_api.api_key = self.slushpool_api_key

        btc_addr_field = self.screen.ids.in_btc_addr
        self.btc_addr = btc_addr_field.text = self.config.get('main', 'btc_addr')
        self.blockchain_api.address = self.btc_addr

        Clock.schedule_interval(self._update, 1)

        self.config.orientation = 2

        return self.screen

    def _update(self, *args):
        self.counter += 1
        if self.counter < int(self.update_interval) + 5:
            return
        self.counter = 0
        self.update()

    def update(self, *args):
        self.last_update = strftime("%H:%M")

        self.slushpool_spinner = True
        self.blockchain_spinner = True

        if fng := self.altfng_api.get_data():
            self.btc_fng_color = fng['color']
            self.btc_fng_icon = fng['icon']

        if balance := self.blockchain_api.get_data():
            self.btc_balance = balance['btc_balance']
            self.usd_btc_balance = balance['usd_balance']
            self.btc_usd = balance['btc_usd_price']
            self.blockchain_spinner = False

        if slush := self.slush_api.get_data():
            self.slushpool_reward = slush['confirmed_reward']
            self.slushpool_reward_confirmed = slush['unconfirmed_reward']
            self.slushpool_hashrate = slush['hash_rate_scoring'] / 1000
            self.slushpool_spinner = False
