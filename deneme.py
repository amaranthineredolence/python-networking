import tkinter as tk
from tkinter import filedialog
import paramiko
import threading
import getpass
import logging

logging.basicConfig(filename='config_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class NetworkConfigurator:
    def __init__(self, master):
        self.master = master
        self.master.title("Network Device Configurator")

        # Variables to store user inputs
        self.username = tk.StringVar()
        self.password = tk.StringVar()
        self.key_path = tk.StringVar()
        self.device_file_path = tk.StringVar()
        self.config_commands_file_path = tk.StringVar()

        # GUI elements
        tk.Label(master, text="Username:").grid(row=0, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=self.username).grid(row=0, column=1, sticky=tk.W)

        tk.Label(master, text="Password:").grid(row=1, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=self.password, show="*").grid(row=1, column=1, sticky=tk.W)

        tk.Label(master, text="SSH Key Path:").grid(row=2, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=self.key_path).grid(row=2, column=1, sticky=tk.W)
        tk.Button(master, text="Browse", command=self.browse_key).grid(row=2, column=2, sticky=tk.W)

        tk.Label(master, text="Device File Path:").grid(row=3, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=self.device_file_path).grid(row=3, column=1, sticky=tk.W)
        tk.Button(master, text="Browse", command=self.browse_device_file).grid(row=3, column=2, sticky=tk.W)

        tk.Label(master, text="Config Commands File Path:").grid(row=4, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=self.config_commands_file_path).grid(row=4, column=1, sticky=tk.W)
        tk.Button(master, text="Browse", command=self.browse_config_commands_file).grid(row=4, column=2, sticky=tk.W)

        tk.Button(master, text="Configure Devices", command=self.configure_devices).grid(row=5, column=0, columnspan=3)

    def browse_key(self):
        key_path = filedialog.askopenfilename(filetypes=[("SSH Key Files", "*.pem;*.key")])
        if key_path:
            self.key_path.set(key_path)

    def browse_device_file(self):
        device_file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if device_file_path:
            self.device_file_path.set(device_file_path)

    def browse_config_commands_file(self):
        config_commands_file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if config_commands_file_path:
            self.config_commands_file_path.set(config_commands_file_path)

    def configure_devices(self):
        username = self.username.get()
        password = self.password.get()
        key_path = self.key_path.get()
        device_file_path = self.device_file_path.get()
        config_commands_file_path = self.config_commands_file_path.get()

        try:
            with open(device_file_path, 'r') as device_file:
                devices = device_file.read().splitlines()

            with open(config_commands_file_path, 'r') as commands_file:
                commands = commands_file.read().splitlines()

            for device in devices:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    if key_path:
                        private_key = paramiko.RSAKey(filename=key_path)
                        ssh.connect(device, username=username, pkey=private_key)
                    else:
                        ssh.connect(device, username=username, password=password)

                    for command in commands:
                        stdin, stdout, stderr = ssh.exec_command(command)
                        logging.info(f"Device: {device}, Command: {command}, Status: Success")

                    ssh.close()

                except Exception as e:
                    logging.error(f"Device: {device}, Error: {str(e)}")
                    continue

        except Exception as e:
            logging.error(f"Error: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkConfigurator(root)
    root.mainloop()
