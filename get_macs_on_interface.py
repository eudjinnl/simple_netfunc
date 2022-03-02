import json
from pathlib import Path
import pprint

import pandas as pd
from devactions import Host, Device, credentials_input


def count_macs_on_interface(mac_table):
    '''
    mac_table = [{'active': True,
                  'interface': 'Gi1/1/1',
                  'last_move': -1.0,
                  'mac': 'AA:AA:AA:AA:AA:01',
                  'moves': -1,
                  'static': False,
                  'vlan': 990},
                  'active': True,
                  'interface': 'Gi1/0/24',
                  'last_move': -1.0,
                  'mac': 'AA:AA:AA:AA:AA:02',
                  'moves': -1,
                  'static': False,
                  'vlan': 997},
                  {'active': True,
                  'interface': 'Gi1/1/1',
                  'last_move': -1.0,
                  'mac': 'AA:AA:AA:AA:AA:01',
                  'moves': -1,
                  'vlan': 999}]
    
    '''
    mac_on_interface = {}
    mac_count = []
    for mac in mac_table:
        if mac['interface']:
            mac_on_interface.setdefault(mac['interface'],set())
            mac_on_interface[mac['interface']].add(mac['mac'])
    
    for int, macs in mac_on_interface.items():
        macs_on_int = {}
        if len(macs) > 1:
            macs_on_int["interface"] = int
            macs_on_int["mac_amount"] = len(macs)
            mac_count.append(macs_on_int)
            
    return mac_count
    

if __name__ == "__main__":

    data_path = Path("data\CDP_Neighbors")
    file = Path("Omsk_Hosts CDP-2022-03-01.json")
    with open(Path(data_path,file)) as f:
        host_data = json.load(f)

    dev_ip = input('Enter device ip to start from: ')
    username, password, optional_args = credentials_input()
    
    mac_count_per_host_list = []
    for host in host_data:
        host_mac_count ={}
        try:
            print(f'Connecting to device {host["name"]}')
            with Device(host['ip'], username, password, optional_args=optional_args) as device:
                print('  getting mac table')
                mac_table = device.mac_address_table
                print('  counting mac addresses')
                mac_count = count_macs_on_interface(mac_table)
                host_mac_count['name'] = host['name']
                host_mac_count['ip'] = host['ip']
                host_mac_count['mac_count'] = mac_count
                mac_count_per_host_list.append(host_mac_count)
        except:
            pass
    

    # pprint.pprint(mac_count_per_host_list)
    with open(Path(data_path,"host_mac_count.json"), "w") as f:
        json.dump(mac_count_per_host_list, f, indent=4)
    
    df_list = []
    for host in mac_count_per_host_list:
        for interface in host['mac_count']:
            host_data = {}
            host_data['name'] = host['name']
            host_data['ip'] = host['ip']
            host_data['interface'] = interface['interface']
            host_data['mac_amount'] = interface['mac_amount']
            df_list.append(host_data)
    
    df_data = pd.DataFrame.from_dict(df_list)
    df_data.to_excel(Path(data_path,'mac_count.xlsx'), index=False)
            