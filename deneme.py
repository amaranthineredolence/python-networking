import tkinter as tk
from tkinter import filedialog
from threading import Thread
import paramiko
import logging
import time

class NetworkConfiguratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Configurator")

        # Variables
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.key_path_var = tk.StringVar()
        self.use_key_var = tk.BooleanVar(value=False)

        # GUI Elements
        tk.Label(root, text="Username:").grid(row=0, column=0, sticky=tk.E)
        tk.Entry(root, textvariable=self.username_var).grid(row=0, column=1)

        tk.Label(root, text="Password:").grid(row=1, column=0, sticky=tk.E)
        tk.Entry(root, textvariable=self.password_var, show='*').grid(row=1, column=1)

        tk.Checkbutton(root, text="Use SSH Key", variable=self.use_key_var, command=self.toggle_key_entry).grid(row=2, column=0, columnspan=2)

        tk.Label(root, text="Key Path:").grid(row=3, column=0, sticky=tk.E)
        self.key_entry = tk.Entry(root, textvariable=self.key_path_var, state=tk.DISABLED)
        self.key_entry.grid(row=3, column=1)
        tk.Button(root, text="Browse", command=self.browse_key).grid(row=3, column=2)

        tk.Label(root, text="Config File:").grid(row=4, column=0, sticky=tk.E)
        self.config_entry = tk.Entry(root, state=tk.DISABLED)
        self.config_entry.grid(row=4, column=1)
        tk.Button(root, text="Browse", command=self.browse_config).grid(row=4, column=2)

        tk.Label(root, text="IP File:").grid(row=5, column=0, sticky=tk.E)
        self.ip_entry = tk.Entry(root, state=tk.DISABLED)
        self.ip_entry.grid(row=5, column=1)
        tk.Button(root, text="Browse", command=self.browse_ip).grid(row=5, column=2)

        tk.Button(root, text="Start Configuration", command=self.start_configuration).grid(row=6, column=0, columnspan=3)

    def toggle_key_entry(self):
        state = tk.NORMAL if self.use_key_var.get() else tk.DISABLED
        self.key_entry.config(state=state)

    def browse_key(self):
        key_path = filedialog.askopenfilename(filetypes=[("Private Key Files", "*.pem")])
        if key_path:
            self.key_path_var.set(key_path)

    def browse_config(self):
        config_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if config_path:
            self.config_entry.insert(0, config_path)

    def browse_ip(self):
        ip_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if ip_path:
            self.ip_entry.insert(0, ip_path)

    def configure_device(self, ip, username, password, key_filename, config):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if key_filename:
                ssh.connect(ip, username=username, key_filename=key_filename, timeout=5)
            else:
                ssh.connect(ip, username=username, password=password, timeout=5)

            # Apply configuration
            ssh.exec_command(config)
            print(f"Configuration applied successfully to {ip}")

            # Close SSH connection
            ssh.close()
            return True
        except Exception as e:
            print(f"Failed to configure {ip}: {e}")
            return False

    def start_configuration(self):
        # Read credentials and configuration file paths
        username = self.username_var.get()
        password = self.password_var.get()
        key_filename = self.key_path_var.get() if self.use_key_var.get() else None
        config_path = self.config_entry.get()
        ip_path = self.ip_entry.get()

        # Read configuration from config.txt
        config = read_file(config_path)

        # Read IP addresses from IP.txt
        ip_addresses = read_lines(ip_path)

        # Setup logging
        setup_logging()

        def configure_devices():
            while True:
                for ip in ip_addresses:
                    ip = ip.strip()  # Remove leading/trailing whitespaces
                    success = self.configure_device(ip, username, password, key_filename, config)

                    # Log the result
                    log_message = f"{ip}: Configuration {'successful' if success else 'failed'}"
                    logging.info(log_message)

                # Sleep for 10 seconds before trying again
                time.sleep(10)

        # Run configuration in a separate thread
        config_thread = Thread(target=configure_devices)
        config_thread.start()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def read_lines(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def setup_logging():
    logging.basicConfig(
        filename='config_log.txt',
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkConfiguratorGUI(root)
    root.mainloop()
