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

logging.info(f"Username: {user}, Switches: {list_of_switches}")

for switch in list_of_switches:
    network_device = {
        "host": switch,
        "username": user,
        "password": password,
    }

    logging.info(f"Connecting to {switch} with username {user}")

    try:
        # Detect the device type
        detector = SSHDetect(**network_device)
        device_type = detector.autodetect()

        # Update the network_device dictionary with the detected device_type
        network_device["device_type"] = device_type

        # Connect to the device
        connect_to_device = ConnectHandler(**network_device)
        connect_to_device.enable()

        list_of_commands = ["show run | i hostname", "show ver"]

        with open(f"#/path to the test log file/#", "a") as f:
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

    except Exception as e:
        logging.error(f"Failed to connect to {switch}: {str(e)}")
        print(f"\nFailed to connect to {switch}")

print("\nComplete")
