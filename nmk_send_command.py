from devactions import Host, credentials_input, nmk_send_conf_command
from get_cdp_neighbors import get_hosts_cdp_neighbors

PATTERNS = {'C9200L'}

connection_params = {
                    'device_type': 'cisco_ios',
                    'host': '',
                    'username': '',
                    'password': '',
                    'secret': '',
                    'verbose': 'True'
                    }

with open("Cisco_commands.txt") as f:
    commands = f.read().splitlines()

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
    else:
        connection_params['host'] = host.ip
        output = nmk_send_conf_command(connection_params, commands)
        print(output)

# commands = ['username r4 secret r1']
# output = nmk_send_conf_command(connection_params, commands)
# print(output)
