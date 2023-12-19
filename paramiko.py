import os
import paramiko
import logging
import tkinter as tk
from tkinter import filedialog

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
        # Choose between password and key based on user input
        if password:
            transport = paramiko.Transport((switch, 22))
            transport.connect(username=user, password=password)
        elif key_file_path:
            private_key = paramiko.RSAKey(filename=key_file_path)
            transport = paramiko.Transport((switch, 22))
            transport.connect(username=user, pkey=private_key)
        else:
            print("Please provide either a password or an SSH key.")
            return

        logging.info(f"Connecting to {switch} with username {user}")

        try:
            # Create an SSH client
            ssh = paramiko.SSHClient()
            ssh._transport = transport

            # Open a log file for each switch
            with open(f"logs/{switch}_log.txt", "a") as f:
                f.write("\n")
                f.write(switch + "#" + str(list_of_commands))
                f.write("\n")

                # Use exec_command for sending commands
                for command in list_of_commands:
                    stdin, stdout, stderr = ssh.exec_command(command)
                    output = stdout.read().decode('utf-8')
                    f.write(output)

                f.write(switch + "#")
                f.write("\n" * 3)
                f.write("\nEND of this device/END of this device/END of this device" * 4)
                f.write("\n" * 3)

            print(f"\nConfiguration saved for {switch}")

        except Exception as e:
            logging.error(f"Failed to connect to {switch} with error: {str(e)}")
            print(f"\nFailed to connect to {switch}")

        finally:
            # Close the SSH connection
            ssh.close()

    print("\nFinished")

# GUI setup
root = tk.Tk()
root.title("Network Configuration Script")

file_path_label = tk.Label(root, text="Enter the path to the txt file containing IP addresses:")
file_path_label.pack()
file_path_entry = tk.Entry(root)
file_path_entry.pack()
file_path_button = tk.Button(root, text="Browse", command=lambda: file_path_entry.insert(tk.END, filedialog.askopenfilename()))
file_path_button.pack()

commands_file_path_label = tk.Label(root, text="Enter the path to the txt file containing commands:")
commands_file_path_label.pack()
commands_file_path_entry = tk.Entry(root)
commands_file_path_entry.pack()
commands_file_path_button = tk.Button(root, text="Browse", command=lambda: commands_file_path_entry.insert(tk.END, filedialog.askopenfilename()))
commands_file_path_button.pack()

# Username, Password, and SSH Key file path
username_label = tk.Label(root, text="What is the username:")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

password_label = tk.Label(root, text="What is the password (leave blank for SSH key):")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

key_file_path_label = tk.Label(root, text="Enter the path to the SSH key file (optional):")
key_file_path_label.pack()
key_file_path_entry = tk.Entry(root)
key_file_path_entry.pack()
key_file_path_button = tk.Button(root, text="Browse", command=lambda: key_file_path_entry.insert(tk.END, filedialog.askopenfilename()))
key_file_path_button.pack()

# Run button
run_button = tk.Button(root, text="Run Script", command=run_script)
run_button.pack()


root.mainloop()
