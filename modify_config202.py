import os
import netmiko
from netmiko import ConnectHandler, SSHDetect
import logging
import getpass

logging.basicConfig(filename='script_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def get_username():
    result = os.popen("whoami").read().strip()
    username = result.split('\\')[-1]
    return username

local_computer_username = get_username()

list_of_switches = []

file_path = input("Enter the path to the txt file containing IP addresses: ")
with open(file_path, 'r') as file:
    list_of_switches = [line.strip() for line in file.readlines()]

user = input("What is the username: ")
password = getpass.getpass("What is the password: ")

commands_file_path = input("Enter the path to the txt file containing commands: ")
with open(commands_file_path, 'r') as commands_file:
    list_of_commands = [line.strip() for line in commands_file.readlines()]

logging.info(f"Username: {user}, Switches: {list_of_switches}, Commands: {list_of_commands}")

for switch in list_of_switches:
    network_device = {
        "host": switch,
        "username": user,
        "password": password,
    }

    logging.info(f"Connecting to {switch} with username {user}")

    try:
        # Try connecting with various device types
        for device_type in ["cisco_ios", "cisco_xe", "cisco_asa", "cisco_nxos", "cisco_ftd", "cisco_s200", "cisco_s300", "cisco_tp", "cisco_viptela", "cisco_wlc", "cisco_xr", "dell_dnos9", "dell_force10", "dell_isilon", "dell_os10", "dell_os6", "dell_os9", "dell_powerconnect", "dell_sonic"]:
            network_device["device_type"] = device_type
            connect_to_device = ConnectHandler(**network_device)
            connect_to_device.enable()

            with open(f"logs/{switch}_log.txt", "a") as f:
                f.write("\n")
                f.write(switch + "#" + str(list_of_commands))
                f.write("\n")
                for command in list_of_commands:
                    output = connect_to_device.send_command(command)
                    f.write(output)
                    f.write("\n")

                f.write(switch + "#")
                f.write("\n" * 3)
                f.write("\nEND of this device/END of this device/END of this device" * 4)
                f.write("\n" * 3)

            print(f"\nConfiguration saved for {switch}")
            break  # Break if successful connection

    except Exception as e:
        logging.error(f"Failed to connect to {switch} with error: {str(e)}")
        print(f"\nFailed to connect to {switch}")

print("\nComplete")
