from simple_netfunc import nmk_send_conf_command

connection_params = {
                    'device_type': 'cisco_ios',
                    'host': '10.1.1.3',
                    'username': 'cisco',
                    'password': 'cisco',
                    'secret': 'cisco',
                    'verbose': 'True'
                    }

commands = ['username r4 secret r1']
output = nmk_send_conf_command(connection_params, commands)
print(output)
