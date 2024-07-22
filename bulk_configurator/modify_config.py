import os
import netmiko
from netmiko import ConnectHandler, SSHDetect
import logging
import getpass
#A network automation tool that uses the Netmiko library to connect to network devices, retrieve specific information, and save the configuration details to a local file.

# Configure logging
logging.basicConfig(filename='script_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def get_username():
    result = os.popen("whoami").read().strip()
    username = result.split('\\')[-1]
    return username
#Uses the whoami command to get the current username of the local computer user.

local_computer_username = get_username()

list_of_switches = []

# Read IP addresses from a txt file
file_path = input("Enter the path to the txt file containing IP addresses: ")
with open(file_path, 'r') as file:
    list_of_switches = [line.strip() for line in file.readlines()]
#Retrieves the local computer username using the get_username function.
#Asks the user for the path to a text file containing a list of IP addresses (presumably, network switches).

user = input("What is the username: ")
password = getpass.getpass("What is the password: ")
#Prompts the user for their username and securely prompts for their password.

commands_file_path = input("Enter the path to the txt file containing commands: ")
with open(commands_file_path, 'r') as commands_file:
    list_of_commands = [line.strip() for line in commands_file.readlines()]

# Log user input
logging.info(f"Username: {user}, Switches: {list_of_switches}, Commands: {list_of_commands}")
#Logs the entered username and the list of switches.

for switch in list_of_switches:
    network_device = {
        "host": switch,
        "username": user,
        "password": password,
    }
#Iterates over each switch in the list and creates a dictionary with connection details.
    
# Log connection attempt
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
#Attempts to connect to the switch using Netmiko.
#Executes a couple of commands and writes the results to a file.
    
    except Exception as e:
        logging.error(f"Failed to connect to {switch} with error: {str(e)}")
        print(f"\nFailed to connect to {switch}")
        
#Log connection error
#Logs any connection errors and prints a failure message.

print("\nComplete")
