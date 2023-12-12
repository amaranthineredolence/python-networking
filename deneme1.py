import os
import netmiko
from netmiko import ConnectHandler
import logging
import getpass
import tkinter as tk
from tkinter import filedialog

logging.basicConfig(filename='script_log.txt', level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')

def get_username():
    result = os.popen("whoami").read().strip()
    username = result.split('\\')[-1]
    return username

def run_script():
    list_of_switches = []
    file_path = file_path_entry.get()
    user = username_entry.get()
    key_file_path = key_file_path_entry.get()
    commands_file_path = commands_file_path_entry.get()

    with open(file_path, 'r') as file:
        list_of_switches = [line.strip() for line in file.readlines()]

    with open(commands_file_path, 'r') as commands_file:
        list_of_commands = [line.strip() for line in commands_file.readlines()]

    logging.info(f"Username: {user}, Switches: {list_of_switches}, Commands: {list_of_commands}")

    for switch in list_of_switches:
        network_device = {
            "device_type": "cisco_ios",
            "host": switch,
            "username": user,
            "key_file": key_file_path,  # Use key_file for SSH key authentication
        }

        logging.info(f"Connecting to {switch} with username {user}")

        try:
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

        except Exception as e:
            logging.error(f"Failed to connect to {switch} with error: {str(e)}")
            print(f"\nFailed to connect to {switch}")

    print("\nComplete")

# GUI setup
root = tk.Tk()
root.title("Network Configuration Script")

# File paths
file_path_label = tk.Label(root, text="Enter the path to the txt file containing IP addresses:")
file_path_label.pack()
file_path_entry = tk.Entry(root)
file_path_entry.pack()
file_path_button = tk.Button(root, text="Browse", command=lambda: file_path_entry.insert(tk.END, filedialog.askopenfilename()))
file_path_button.pack()

key_file_path_label = tk.Label(root, text="Enter the path to the private key file:")
key_file_path_label.pack()
key_file_path_entry = tk.Entry(root)
key_file_path_entry.pack()
key_file_path_button = tk.Button(root, text="Browse", command=lambda: key_file_path_entry.insert(tk.END, filedialog.askopenfilename()))
key_file_path_button.pack()

commands_file_path_label = tk.Label(root, text="Enter the path to the txt file containing commands:")
commands_file_path_label.pack()
commands_file_path_entry = tk.Entry(root)
commands_file_path_entry.pack()
commands_file_path_button = tk.Button(root, text="Browse", command=lambda: commands_file_path_entry.insert(tk.END, filedialog.askopenfilename()))
commands_file_path_button.pack()

# Username
username_label = tk.Label(root, text="What is the username:")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

# Run button
run_button = tk.Button(root, text="Run Script", command=run_script)
run_button.pack()

root.mainloop()
