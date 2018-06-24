"""
This module contains class to manage RPC communications (Telegram, Slack, Rest ....)
"""
import logging
from typing import List, Dict

from freqtrade.rpc.rpc import RPC

logger = logging.getLogger(__name__)


class RPCManager(object):
    """
    Class to manage RPC objects (Telegram, Slack, ...)
    """
    def __init__(self, freqtrade) -> None:
        """ Initializes all enabled rpc modules """
        self.registered_modules: List[RPC] = []

        # Enable telegram
        if freqtrade.config.get('telegram', {}).get('enabled', False):
            logger.info('Enabling rpc.telegram ...')
            from freqtrade.rpc.telegram import Telegram
            self.registered_modules.append(Telegram(freqtrade))

        # Enable local rest api server for cmd line control
        if freqtrade.config.get('api_server', {}).get('enabled', False):
            logger.info('Enabling rpc.api_server')
            from freqtrade.rpc.api_server import ApiServer
            self.registered_modules.append(ApiServer(freqtrade))

    def cleanup(self) -> None:
        """ Stops all enabled rpc modules """
        logger.info('Cleaning up rpc modules ...')
        while self.registered_modules:
            mod = self.registered_modules.pop()
            logger.debug('Cleaning up rpc.%s ...', mod.name)
            mod.cleanup()
            del mod

    def send_msg(self, msg: Dict[str, str]) -> None:
        """
        Send given message to all registered rpc modules.
        A message consists of one or more key value pairs of strings.
        e.g.:
        {
            'status': 'stopping bot'
        }
        """
        logger.info('Sending rpc message: %s', msg)
        for mod in self.registered_modules:
            logger.debug('Forwarding message to rpc.%s', mod.name)
            mod.send_msg(msg)
