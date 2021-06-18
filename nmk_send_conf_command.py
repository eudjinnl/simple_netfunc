"""
Build list of all devices using cdp crawling.
Send commands from  _cisco_commands.txt file to devices defined in PATTERNS.
By default save running-config to memory.
    Config saving can be overridden by adding variable write_memory=False to nmk_send_conf_command function
Backup config as hostname-YYYY-MM-DD text file to the path defined in file _backup_path.txt. 
If there is no the file or it is empty config files will be written in working directory.
"""

from datetime import datetime
from pathlib import Path

import yaml
import sys
from devactions import Device, credentials_input, nmk_send_conf_command, nmk_send_command
from get_cdp_neighbors import get_hosts_cdp_neighbors

# patterns of device models (platforms) which commands should be sent to
config_file = 'nmk_send_conf_command_config.yml'

# connection_params = {
#                     'device_type': 'cisco_ios',
#                     'host': '',
#                     'username': '',
#                     'password': '',
#                     'secret': '',
#                     'verbose': 'True'
#                     }

try:
    # Open file with config. 
    with open(config_file, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)
except:
    print(f'No configuration file, "{config_file}"')
    sys.exit()

try:
    backup_path = Path(cfg['parameters']['paths_and_files']['backup_path'])
except:
    print(f'No backup path has been found in confugutation file {config_file}')
    print('parameters:')
    print('  paths_and_files:')
    print('    backup_path: "SOME\PATH\HERE"\n')
    sys.exit()

try:
    file_with_commands = Path(cfg['parameters']['paths_and_files']['file_with_commands'])
except:
    print(f'No files with commands has been found in confugutation file {config_file}')
    print('parameters:')
    print('  paths_and_files:')
    print('    file_with_commands: "SOME\PATH\\file_with_commands.txt"\n')
    sys.exit()

try:
    device_patterns = set(cfg['parameters']['device_patterns'].split(','))
except:
    print(f'No device patterns has been found in confugutation file {config_file}')
    print('parameters:')
    print('  device_patterns: some,patterns,here\n')
    sys.exit()

try:
    connection_params = cfg['parameters']['connection_params']
except:
    print(f'No connection parameters for netmiko has been found in confugutation file {config_file}')
    print('parameters:')
    print("""  connection_params: {
                     'device_type': 'netmiko_device_type',
                     'host': '',
                     'username': '',
                     'password': '',
                     'secret': '',
                     'verbose': 'True'
                     }\n""")
    sys.exit()

try:
    write_memory = cfg['parameters']['write_memory']
except:
    print(f'No "write_memory" parameter has been found in confugutation file {config_file}')
    print('  "write_memory" is set to True')
    write_memory = True




try:
    # Open file with commands. 
    with open(file_with_commands, "r") as f:
        commands = f.read().splitlines()
except:
    print('No file _cisco_commands.txt with commands')
    sys.exit()


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

processed_hosts = []

for host in hosts_cdp:
    if device_patterns:
        # If PATTERNS exist send command only to devices which match the PATTERNS
        for pattern in device_patterns:
            if pattern in host.platform or pattern in host.name or pattern == 'any':
                connection_params['host'] = host.ip
                print(f'Connecting to host {host.name} {host.ip}\n')
                # Sending commands to device
                output = nmk_send_conf_command(connection_params, commands,write_memory = write_memory)
                print(output)
                # Getting hostname from device using NAPALM
                with Device(host.ip, username, password, optional_args=optional_args) as device:
                    hostname  = device.facts['hostname']
                filename = f'{hostname}-{year}-{month}-{day}' # Compile filename
                full_filename = Path(backup_path, filename) # Compile filename
                command = 'sh run' 
                # Backuping config
                result = nmk_send_command(connection_params, command=command)
                # Writing config to the file
                with open(full_filename, 'w') as backup:
                    backup.write(result)
                    print(f'Backup of {hostname} completed successfully\n')
                processed_hosts.append(hostname)

print(f'Processed hosts: {len(processed_hosts)}\n')
for host in processed_hosts:
    print(host)

    # else:
    #     # If PATTERNS don't exist send commands to each device from the list
    #     connection_params['host'] = host.ip
    #     # Sending commands to device
    #     output = nmk_send_conf_command(connection_params, commands)
    #     print(output)
    #     # Getting hostname from device using NAPALM
    #     with Device(host.ip, username, password, optional_args=optional_args) as device:
    #         hostname = device.facts['hostname']
    #     filename = f'{backup_path}{hostname}-{year}-{month}-{day}' # Compile filename
    #     command = 'sh run'
    #     result = nmk_send_command(connection_params, command=command)
    #     # Writing config to the file
    #     with open(filename, 'w') as backup:
    #         backup.write(result)
    #         print(f'Backup of {hostname} completed successfully\n')

