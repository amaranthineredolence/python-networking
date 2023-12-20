import paramiko
import getpass
import logging
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor

# ... (Previous code remains unchanged)

def configure_device(ip, username, password=None, private_key=None, commands=None):
    try:
        # Create an SSH client
        ssh_client = paramiko.SSHClient()

        # Automatically add the server's host key
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the device
        if private_key:
            # Use key-based authentication
            private_key = paramiko.RSAKey(filename=private_key)
            ssh_client.connect(ip, username=username, pkey=private_key, timeout=10)
        elif password:
            # Use password authentication
            ssh_client.connect(ip, username=username, password=password, timeout=10)
        else:
            raise ValueError("Either password or private key must be provided.")

        logging.info(f"Connected to {ip}")

        # Execute commands
        if commands:
            for command in commands:
                stdin, stdout, stderr = ssh_client.exec_command(command)
                output = stdout.read().decode()
                logging.info(f"Command '{command}' output for {ip}:\n{output}")

        # Close the SSH connection
        ssh_client.close()
        logging.info(f"Configuration complete for device {ip}")

    except Exception as e:
        error_message = f"Error configuring device {ip}: {str(e)}"
        logging.error(error_message)
        print(error_message)

class ConfiguratorGUI:

      def __init__(self, root):
        self.root = root
        self.root.title("Network Device Configurator")

        self.create_widgets()

    def create_widgets(self):
        # Label and Entry for SSH username
        tk.Label(self.root, text="SSH Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.root)
        self.username_entry.grid(row=0, column=1)

        # Label and Entry for SSH password
        tk.Label(self.root, text="SSH Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.root, show='*')
        self.password_entry.grid(row=1, column=1)

        # Label and Entry for private key path
        tk.Label(self.root, text="Private Key Path:").grid(row=2, column=0)
        self.key_path_entry = tk.Entry(self.root)
        self.key_path_entry.grid(row=2, column=1)

        # Button to browse for private key file
        tk.Button(self.root, text="Browse", command=self.browse_private_key).grid(row=2, column=2)

        # Label and Entry for device IPs file path
        tk.Label(self.root, text="Device IPs File:").grid(row=3, column=0)
        self.device_ips_entry = tk.Entry(self.root)
        self.device_ips_entry.grid(row=3, column=1)

        # Button to browse for device IPs file
        tk.Button(self.root, text="Browse", command=self.browse_device_ips).grid(row=3, column=2)

        # Label and Entry for commands file path
        tk.Label(self.root, text="Commands File:").grid(row=4, column=0)
        self.commands_entry = tk.Entry(self.root)
        self.commands_entry.grid(row=4, column=1)

        # Button to browse for commands file
        tk.Button(self.root, text="Browse", command=self.browse_commands).grid(row=4, column=2)

        # Button to start configuration
        tk.Button(self.root, text="Start Configuration", command=self.start_configuration).grid(row=5, column=1)

    def browse_private_key(self):
        private_key_path = filedialog.askopenfilename(title="Select Private Key File", filetypes=[("Private Key Files", "*.pem;*.key")])
        self.key_path_entry.delete(0, tk.END)
        self.key_path_entry.insert(tk.END, private_key_path)

    def browse_device_ips(self):
        device_ips_path = filedialog.askopenfilename(title="Select Device IPs File", filetypes=[("Text Files", "*.txt")])
        self.device_ips_entry.delete(0, tk.END)
        self.device_ips_entry.insert(tk.END, device_ips_path)

    def browse_commands(self):
        commands_path = filedialog.askopenfilename(title="Select Commands File", filetypes=[("Text Files", "*.txt")])
        self.commands_entry.delete(0, tk.END)
        self.commands_entry.insert(tk.END, commands_path)

    def start_configuration(self):
        # Read input values
        username = self.username_entry.get()
        password = self.password_entry.get()
        private_key_path = self.key_path_entry.get()
        device_ips_path = self.device_ips_entry.get()
        commands_path = self.commands_entry.get()

        # Read device IPs from a file
        with open(device_ips_path, 'r') as f:
            device_ips = f.read().splitlines()

        # Read commands from a file
        with open(commands_path, 'r') as f:
            commands = f.read().splitlines()

        # Configure devices concurrently
        with ThreadPoolExecutor(max_workers=len(device_ips)) as executor:
            futures = [executor.submit(configure_device, ip, username, password=password, private_key=private_key_path, commands=commands) for ip in device_ips]

            # Wait for all tasks to complete
            for future in futures:
                future.result()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfiguratorGUI(root)
    root.mainloop()
