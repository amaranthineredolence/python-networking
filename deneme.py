import tkinter as tk
from tkinter import filedialog
import paramiko
import logging
import threading

def configure_device_ssh(ip, username, password=None, key_filename=None, commands=None):
    try:
        # Create SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the device
        if key_filename:
            ssh.connect(ip, username=username, key_filename=key_filename)
        else:
            ssh.connect(ip, username=username, password=password)

        # Execute commands
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            logging.info(f"Command: {command}\nOutput: {stdout.read().decode()}")

        # Close the SSH connection
        ssh.close()

        return True
    except Exception as e:
        logging.error(f"Failed to configure device {ip}: {str(e)}")
        return False

def browse_file_path(entry_widget):
    file_path = filedialog.askopenfilename()
    entry_widget.delete(0, tk.END)
    entry_widget.insert(0, file_path)

def configure_devices():
    # Read input values from the GUI
    selected_username = username_entry.get()
    selected_password = password_entry.get()
    selected_key_filename = key_filename_entry.get()
    ip_file_path = ip_file_path_entry.get()
    commands_file_path = commands_file_path_entry.get()

    # Configure logging
    logging.basicConfig(filename='config_script.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Read device IPs from file
    with open(ip_file_path, 'r') as file:
        device_ips = file.read().splitlines()

    # Read commands from file
    with open(commands_file_path, 'r') as file:
        commands = file.read().splitlines()

    # Configure devices in a separate thread
    def configure_devices_thread():
        for ip in device_ips:
            success = configure_device_ssh(ip, selected_username, password=selected_password, key_filename=selected_key_filename, commands=commands)
            if success:
                logging.info(f"Successfully configured device {ip}")
                update_status(f"Successfully configured device {ip}")
            else:
                logging.error(f"Failed to configure device {ip}")
                update_status(f"Failed to configure device {ip}")

    # Start the configuration thread
    threading.Thread(target=configure_devices_thread).start()

def update_status(message):
    status_label.config(text=message)

# Create the main window
root = tk.Tk()
root.title("Network Device Configurator")

# Create and place widgets
tk.Label(root, text="Username:").grid(row=0, column=0, sticky=tk.E)
username_entry = tk.Entry(root)
username_entry.grid(row=0, column=1)

tk.Label(root, text="Password:").grid(row=1, column=0, sticky=tk.E)
password_entry = tk.Entry(root, show='*')
password_entry.grid(row=1, column=1)

tk.Label(root, text="SSH Key File (optional):").grid(row=2, column=0, sticky=tk.E)
key_filename_entry = tk.Entry(root)
key_filename_entry.grid(row=2, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file_path(key_filename_entry)).grid(row=2, column=2)

tk.Label(root, text="IP File Path:").grid(row=3, column=0, sticky=tk.E)
ip_file_path_entry = tk.Entry(root)
ip_file_path_entry.grid(row=3, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file_path(ip_file_path_entry)).grid(row=3, column=2)

tk.Label(root, text="Commands File Path:").grid(row=4, column=0, sticky=tk.E)
commands_file_path_entry = tk.Entry(root)
commands_file_path_entry.grid(row=4, column=1)
tk.Button(root, text="Browse", command=lambda: browse_file_path(commands_file_path_entry)).grid(row=4, column=2)

tk.Button(root, text="Configure Devices", command=configure_devices).grid(row=5, column=0, columnspan=3)

# Status label to show configuration progress
status_label = tk.Label(root, text="")
status_label.grid(row=6, column=0, columnspan=3)

# Start the Tkinter event loop
root.mainloop()
