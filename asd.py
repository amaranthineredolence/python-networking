import os
import netmiko
from netmiko import ConnectHandler
import logging
import tkinter as tk
from tkinter import filedialog
# (PARAMIKO VERSION 2.8.1/ NETMIKO VERSION 3.4.0)

# Set up logging configuration
logging.basicConfig(filename='script_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

# Function to get the current username
def get_username():
    result = os.popen("whoami").read().strip()
    username = result.split('\\')[-1]
    return username

# Function to run the script
def run_script():
    # Initialize variables
    list_of_switches = []
    file_path = file_path_entry.get()
    user = username_entry.get()
    password = password_entry.get()
    key_file_path = key_file_path_entry.get()  # Added SSH key file path entry
    commands_file_path = commands_file_path_entry.get()

    # Read IP addresses from the specified file
    with open(file_path, 'r') as file:
        list_of_switches = [line.strip() for line in file.readlines()]

    # Read commands from the specified file
    with open(commands_file_path, 'r') as commands_file:
        list_of_commands = [line.strip() for line in commands_file.readlines()]

    # Log the script parameters
    logging.info(f"Username: {user}, Switches: {list_of_switches}, Commands: {list_of_commands}")

    # Loop through each switch and execute commands
    for switch in list_of_switches:
        network_device = {
            "host": switch,
            "username": user,
            "device_type": "",  # Initialize device_type to be set later
        }

        # Choose between password and key based on user input
        if password:
            network_device["password"] = password
        elif key_file_path:
            network_device["key_file"] = key_file_path
        else:
            print("Please provide either a password or an SSH key.")
            return

        logging.info(f"Connecting to {switch} with username {user}")

        try:
            # Try connecting with various device types
            for device_type in ["cisco_ios", "cisco_xe", "cisco_asa", "cisco_nxos", "cisco_ftd", "cisco_s200", "cisco_s300", "cisco_tp", "cisco_viptela", "cisco_wlc", "cisco_xr", "dell_dnos9", "dell_force10", "dell_isilon", "dell_os10", "dell_os6", "dell_os9", "dell_powerconnect", "dell_sonic"]:
                network_device["device_type"] = device_type
                connect_to_device = ConnectHandler(**network_device)
                connect_to_device.enable()

                # Open a log file for each switch
                with open(f"logs/{switch}_log.txt", "a") as f:
                    f.write("\n")
                    f.write(switch + "#" + str(list_of_commands))
                    f.write("\n")

                    # Use send_config_set for sending configuration changes
                    output = connect_to_device.send_config_set(list_of_commands + [''])  # Add an empty string to simulate Enter key press
                    f.write(output)

                    f.write(switch + "#")
                    f.write("\n" * 3)
                    f.write("\nEND of this device/END of this device/END of this device" * 4)
                    f.write("\n" * 3)

                print(f"\nConfiguration saved for {switch}")
                break  # Break if successful connection

        except Exception as e:
            logging.error(f"Failed to connect to {switch} with error: {str(e)}")
            print(f"\nFailed to connect to {switch}")

    print("\nFinished")

# Rest of your script remains unchanged
