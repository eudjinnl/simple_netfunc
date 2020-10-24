import getpass
import re

from netmiko import ConnectHandler
from napalm import get_network_driver
from dataclasses import dataclass


@dataclass
class Host:
    name : str
    ip : str
    platform : str
    cdp : dict



class Device:

    def __init__(self, ip, username, password, *,optional_args=None, driver_type='ios'):
        klass = get_network_driver(driver_type)
        self._driver = klass(ip, username, password, optional_args=optional_args)

    def __enter__(self):
        self._driver.open()
        return self

    def __exit__(self, *exc_details):
        self._driver.close()

    @property
    def facts(self):
        return self._driver.get_facts()

    @property
    def mac_address_table(self):
        return self._driver.get_mac_address_table()

    def neighbors(self, *, interface=None):
        if interface is None:
            command = 'show cdp neighbors detail'
        else:
            command = f'show cdp neighbors {interface} detail'

        self._driver.cli(['terminal length 0'])
        result = self._driver.cli([command])
        return result[command].split('\n')

    def get_inventory(self):
        command = f'show inventory'

        self._driver.cli(['terminal length 0'])
        result = self._driver.cli([command])
        return result[command].split('\n')

    def send_command(self, *, command=None):
        self._driver.cli(['terminal length 0'])
        result = self._driver.cli(command)
        return result



def credentials_input():
    username = input("Enter Username: ")
    password = getpass.getpass()
    secret = getpass.getpass(prompt = 'Enter enable secret: ')

    optional_args = {}
    if secret:
        optional_args['secret'] = secret
    return username, password, optional_args



def nmk_send_conf_command(connection_params, commands):
    """
    netmiko module is used
    sends configuration commands and saves config to memory in the end
    
    connection_params = {
                    'device_type': 'cisco_ios',
                    'host': '10.1.1.3',
                    'username': 'cisco',
                    'password': 'cisco',
                    'secret': 'cisco'      # optional
                    'port': '22'           # optional, default '22'
                    'verbose': False       # optional, default False
                    }
    
    commands - list of strings. Each string - single command
    """
    connection = ConnectHandler(**connection_params)
    connection.enable()
    
    output = connection.send_config_set(commands)
    outputwr = connection.send_command('write memory')
    connection.disconnect()
    output = output + outputwr
    return output