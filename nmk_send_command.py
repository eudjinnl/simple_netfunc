from datetime import datetime

import sys
from devactions import Host, Device, credentials_input, nmk_send_conf_command, nmk_send_command
from get_cdp_neighbors import get_hosts_cdp_neighbors

PATTERNS = {'WS-C3850'}

connection_params = {
                    'device_type': 'cisco_ios',
                    'host': '',
                    'username': '',
                    'password': '',
                    'secret': '',
                    'verbose': 'True'
                    }

try:
    with open("_cisco_commands.txt") as f:
        commands = f.read().splitlines()
except:
    print('No file _cisco_commands.txt with commands')
    sys.exit()

try:
    with open("_backup_path.txt") as f:
        backup_path = f.read()
except:
    backup_path = ''
    print('No file _backup_path.txt with backup path in it. Config will be saved to working directory' )

now = datetime.now()
year = f'{now.year}'
month = f'{now.month:02d}'
day = f'{now.day:02d}' 

filename = f'{backup_path}-{year}-{month}-{day}'

start_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()

connection_params['username'] = username
connection_params['password'] = password
connection_params['secret'] = optional_args['secret']

hosts_cdp = get_hosts_cdp_neighbors(start_ip, username, password, optional_args)

for host in hosts_cdp:
    if PATTERNS:
        for pattern in PATTERNS:
            if pattern in host.platform:
                connection_params['host'] = host.ip
                output = nmk_send_conf_command(connection_params, commands)
                print(output)
                with Device(host.ip, username, password, optional_args=optional_args) as device:
                    hostname  = device.facts['hostname']
                filename = f'{backup_path}{hostname}-{year}-{month}-{day}'
                command = 'sh run'
                result = nmk_send_command(connection_params, command=command)
                with open(filename, 'w') as backup:
                    backup.write(result)
                    print(f'Backup of {hostname} completed successfully\n')

    else:
        connection_params['host'] = host.ip
        output = nmk_send_conf_command(connection_params, commands)
        print(output)
        with Device(host.ip, username, password, optional_args=optional_args) as device:
            hostname = device.facts['hostname']
        filename = f'{backup_path}{hostname}-{year}-{month}-{day}'
        command = 'sh run'
        result = nmk_send_command(connection_params, command=command)
        with open(filename, 'w') as backup:
            backup.write(result)
            print(f'Backup of {hostname} completed successfully\n')

