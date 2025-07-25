from .commander import Commander
from .logger import Logger
from .proxy import Proxy
from .connector import Connector


class Func:
    def __init__(self):
        self.proxy = Proxy()
        self.connector = Connector()
        self.commander = Commander()
        self.logger = Logger("application").get_logger()
