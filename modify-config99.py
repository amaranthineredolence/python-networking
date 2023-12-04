import os #Provides a way to interact with the operating system.
import netmiko #A multi-vendor library to simplify Paramiko SSH connections to network devices.
from netmiko import ConnectHandler
import logging #Python logging module for generating log information.
import getpass #Allows the script to securely prompt the user for a password.

#A network automation tool that uses the Netmiko library to connect to Cisco IOS devices, retrieve specific information, and save the configuration details to a local file.

# Configure logging
logging.basicConfig(filename='script_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
#Configures logging to write log messages to a file named 'script_log.txt' with a specific format.

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


# Log user input
logging.info(f"Username: {user}, Switches: {list_of_switches}")
#Logs the entered username and the list of switches.

for switch in list_of_switches:
    network_device = {
        "host": switch,
        "username": user,
        "password": password,
        "device_type": "cisco_ios"
    }
#Iterates over each switch in the list and creates a dictionary with connection details.
    
    # Log connection attempt
    logging.info(f"Connecting to {switch} with username {user}")

    try:
        connect_to_device = ConnectHandler(**network_device)
        connect_to_device.enable()

        list_of_commands = ["show run | i hostname", "show ver"]

        with open(f"(/directory to the log file/)", "a") as f:
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
#Attempts to connect to the switch using Netmiko.
#Executes a couple of commands and writes the results to a file.
    
    except Exception as e:
        # Log connection error
        logging.error(f"Failed to connect to {switch}: {str(e)}")
        print(f"\nFailed to connect to {switch}")
#Logs any connection errors and prints a failure message.
print("\nComplete")
