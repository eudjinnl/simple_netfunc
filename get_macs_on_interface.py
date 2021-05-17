import json
from pathlib import Path
import pprint

from devactions import Host, Device, credentials_input


if __name__ == "__main__":

    data_path = Path("data")

    dev_ip = input('Enter device ip to start from: ')
    username, password, optional_args = credentials_input()

    with Device(dev_ip, username, password, optional_args=optional_args) as device:
        mac_table = device.mac_address_table

    mac_on_interface = {}

#     mac_table = [{'active': True,
#   'interface': 'Gi1/1/1',
#   'last_move': -1.0,
#   'mac': 'AA:AA:AA:AA:AA:01',
#   'moves': -1,
#   'static': False,
#   'vlan': 990},
#  {'active': True,
#   'interface': 'Gi1/0/24',
#   'last_move': -1.0,
#   'mac': 'AA:AA:AA:AA:AA:02',
#   'moves': -1,
#   'static': False,
#   'vlan': 997},
#   {'active': True,
#   'interface': 'Gi1/1/1',
#   'last_move': -1.0,
#   'mac': 'AA:AA:AA:AA:AA:03',
#   'moves': -1,
#   'vlan': 999}]

    for mac in mac_table:
        if mac['interface']:
            mac_on_interface.setdefault(mac['interface'],[])
            mac_on_interface[mac['interface']].append(mac['mac'])

    pprint.pprint(mac_on_interface)