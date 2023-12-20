import paramiko
import logging
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
import getpass

# Configure logging
logging.basicConfig(filename='script.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def configure_device(ip, username, password, key_filename, commands):
    try:
        # SSH Connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if key_filename:
            # Use key authentication
            private_key = paramiko.RSAKey(filename=key_filename)
            ssh.connect(ip, username=username, pkey=private_key, timeout=10)
        else:
            # Use password authentication
            ssh.connect(ip, username=username, password=password, timeout=10)

        # Execute configuration commands
        for command in commands:
            stdin, stdout, stderr = ssh.exec_command(command)
            result = stdout.read().decode()
            log_result(ip, username, "Success", f"Command: {command}\nResult: {result}")
            logging.info(f"Command executed on {ip} ({username}): {command}\nResult: {result}")

        # Close the SSH connection
        ssh.close()

    except Exception as e:
        # Log failure details
        log_result(ip, username, "Failure", str(e))
        logging.error(f"Failed to execute commands on {ip} ({username}): {str(e)}")

def log_result(ip, username, status, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {ip} ({username}): {status}\nDetails: {details}\n\n"

    with open("log.txt", "a") as log_file:
        log_file.write(log_entry)

def run_script():
    try:
        # Prompt user for SSH credentials
        username = username_entry.get()
        password = password_entry.get()
        key_filename = filedialog.askopenfilename(title="Select Private Key File", filetypes=[("Key Files", "*.pem;*.ppk")])

        # Read devices and commands from text files
        devices_file = filedialog.askopenfilename(title="Select Devices File", filetypes=[("Text Files", "*.txt")])
        commands_file = filedialog.askopenfilename(title="Select Commands File", filetypes=[("Text Files", "*.txt")])

        devices = [line.split(",") for line in read_file(devices_file)]
        commands = read_file(commands_file)

        # Loop through devices and configure each
        for device_info in devices:
            ip, _, _ = device_info
            configure_device(ip, username, password, key_filename, commands)

        result_label.config(text="Configuration completed. Check log.txt and script.log for details.")

    except Exception as e:
        result_label.config(text=f"Error: {str(e)}")

def read_file(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file.readlines()]

# Create main window
window = tk.Tk()
window.title("SSH Configuration Script")

# Create and pack widgets
tk.Label(window, text="SSH Configuration Script", font=("Helvetica", 16)).pack(pady=10)

tk.Label(window, text="SSH Username:").pack()
username_entry = tk.Entry(window)
username_entry.pack()

tk.Label(window, text="SSH Password:").pack()
password_entry = tk.Entry(window, show="*")
password_entry.pack()

run_button = tk.Button(window, text="Run Script", command=run_script)
run_button.pack(pady=10)

result_label = tk.Label(window, text="")
result_label.pack()

# Start the GUI main loop
window.mainloop()
