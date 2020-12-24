import getpass
import time

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
# Class for interaction with devices. NAPALM module is used to interact
    def __init__(self, ip, username, password, *,optional_args=None, driver_type='ios'):
        """
        NAPALM driver creation
        optional_args variable is a Dictionary with additional connection parameters. 
        Here it used to provide enable secret. For full list of parameters see NAPALM documentation
        """
        klass = get_network_driver(driver_type)
        self._driver = klass(ip, username, password, optional_args=optional_args)

    def __enter__(self):
        # Connecting to device
        self._driver.open()
        return self

    def __exit__(self, *exc_details):
        # Disconnecting from device
        self._driver.close()
        time.sleep(1)

    @property
    def facts(self):
        # Getting facts from device using NAPALM.
        return self._driver.get_facts()

    @property
    def mac_address_table(self):
        # Getting mac address table from device using NAPALM.
        return self._driver.get_mac_address_table()

    def send_command(self, *, command=None):
        """"
        Sending command using NAPALM.
        Doesn't work with configuration commands and some commands of privileged mode either
        command - list of strings where each string - one command 
        Returns output of command
        """
        self._driver.cli(['terminal length 0'])
        result = self._driver.cli(command)
        return result

    def neighbors(self, *, interface=None):
        """
        Getting cdp neighbors device using NAPALM by sending command to device.
        Returns list of strings where every string is a string from output of the command which was sent to device.
        """
        if interface is None:
            # To see whole list of cdp neighbors
            command = 'show cdp neighbors detail'
        else:
            # To see cdp neigbor on specific interface
            command = f'show cdp neighbors {interface} detail'

        self._driver.cli(['terminal length 0'])
        result = self._driver.cli([command])
        return result[command].split('\n')

    def get_inventory(self):
        """
        Getting cdp neighbors device using NAPALM by sending command to device.
        Returns list of strings where every string is a string from output of the command which was sent to device.
        """
        command = f'show inventory'

        self._driver.cli(['terminal length 0'])
        result = self._driver.cli([command])
        return result[command].split('\n')


def credentials_input():
    """Ask for credentials input

    Returns:
        username {string}: username
        password {string}: password
        optional_args {dicrionary}: dictionary of optional arguments. here {'secret':'SECRET_PASSWORD'}
                                    where 'SECRET_PASSWORD' is password for entering to privileged mode ("enable" command)
    """
    # Prompt user to enter credentials
    username = input("Enter Username: ")
    password = getpass.getpass()
    secret = getpass.getpass(prompt = 'Enter enable secret: ')

    optional_args = {}
    if secret:
        optional_args['secret'] = secret
    return username, password, optional_args



def nmk_send_conf_command(connection_params, commands, write_memory=True):
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

    write_memory: if True (default) - config will be saved with "write memory" command
    """
    outputwr = ''
    connection = ConnectHandler(**connection_params)
    connection.enable()
    
    output = connection.send_config_set(commands)
    if write_memory:
        outputwr = connection.send_command('write memory')
    connection.disconnect()
    output = output + outputwr
    return output

def nmk_send_command(connection_params, command):
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
    
    commands - string with single command
    """
    connection = ConnectHandler(**connection_params)
    connection.enable()
    
    output = connection.send_command(command)
    connection.disconnect()
    return output