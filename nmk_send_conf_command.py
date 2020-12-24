"""
Build list of all devices using cdp crawling.
Send commands from  _cisco_commands.txt file to devices defined in PATTERNS.
By default save running-config to memory.
    Config saving can be overridden by adding variable write_memory=False to nmk_send_conf_command function
Backup config as hostname-YYYY-MM-DD text file to the path defined in file _backup_path.txt. 
If there is no the file or it is empty config files will be written in working directory.
"""

from datetime import datetime

import sys
from devactions import Device, credentials_input, nmk_send_conf_command, nmk_send_command
from get_cdp_neighbors import get_hosts_cdp_neighbors

# patterns of device models (platforms) whicch commands should be sent to
PATTERNS = {'C9200L'}

connection_params = {
                    'device_type': 'cisco_ios',
                    'host': '',
                    'username': '',
                    'password': '',
                    'secret': '',
                    'verbose': 'True'
                    }

try:
    # Open file with commands. 
    with open("_cisco_commands.txt") as f:
        commands = f.read().splitlines()
except:
    print('No file _cisco_commands.txt with commands')
    sys.exit()

try:
    #Open file with backup path
    with open("_backup_path.txt") as f:
        backup_path = f.read()
except:
    backup_path = ''
    print('No file _backup_path.txt with backup path in it. Config will be saved to working directory' )

# Getting today date
now = datetime.now()
year = f'{now.year}'
month = f'{now.month:02d}'
day = f'{now.day:02d}' 

# Asking user for ip to start cdp crawlig from and user credentials for accessing devices
start_ip = input('Enter device ip to start from: ')
username, password, optional_args = credentials_input()

connection_params['username'] = username
connection_params['password'] = password
connection_params['secret'] = optional_args['secret']

# Building list of devices by using cdp crawling function
hosts_cdp = get_hosts_cdp_neighbors(start_ip, username, password, optional_args)

for host in hosts_cdp:
    if PATTERNS:
        # If PATTERNS exist send command only to devices which match the PATTERNS
        for pattern in PATTERNS:
            if pattern in host.platform:
                connection_params['host'] = host.ip
                # Sending commands to device
                output = nmk_send_conf_command(connection_params, commands)
                print(output)
                # Getting hostname from device using NAPALM
                with Device(host.ip, username, password, optional_args=optional_args) as device:
                    hostname  = device.facts['hostname']
                filename = f'{backup_path}{hostname}-{year}-{month}-{day}' # Compile filename
                command = 'sh run' 
                # Backupping config
                result = nmk_send_command(connection_params, command=command)
                # Writing config to the file
                with open(filename, 'w') as backup:
                    backup.write(result)
                    print(f'Backup of {hostname} completed successfully\n')

    else:
        # If PATTERNS don't exist send commands to each device from the list
        connection_params['host'] = host.ip
        # Sending commands to device
        output = nmk_send_conf_command(connection_params, commands)
        print(output)
        # Getting hostname from device using NAPALM
        with Device(host.ip, username, password, optional_args=optional_args) as device:
            hostname = device.facts['hostname']
        filename = f'{backup_path}{hostname}-{year}-{month}-{day}' # Compile filename
        command = 'sh run'
        result = nmk_send_command(connection_params, command=command)
        # Writing config to the file
        with open(filename, 'w') as backup:
            backup.write(result)
            print(f'Backup of {hostname} completed successfully\n')

