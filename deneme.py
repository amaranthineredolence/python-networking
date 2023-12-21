import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import paramiko
import threading
import getpass
import logging

class NetworkConfiguratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Configurator")

        self.create_widgets()

    def create_widgets(self):
        # Username
        self.username_label = ttk.Label(self.root, text="Username:")
        self.username_entry = ttk.Entry(self.root)
        self.username_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Password
        self.password_label = ttk.Label(self.root, text="Password:")
        self.password_entry = ttk.Entry(self.root, show="*")
        self.password_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # SSH Key
        self.ssh_key_label = ttk.Label(self.root, text="SSH Key (path):")
        self.ssh_key_entry = ttk.Entry(self.root)
        self.ssh_key_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.ssh_key_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # IP Addresses
        self.ip_label = ttk.Label(self.root, text="IP Addresses (file):")
        self.ip_file_entry = ttk.Entry(self.root)
        self.ip_file_button = ttk.Button(self.root, text="Browse", command=self.browse_ip_file)
        self.ip_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.ip_file_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.ip_file_button.grid(row=3, column=2, padx=5, pady=5, sticky="w")

        # Commands
        self.commands_label = ttk.Label(self.root, text="Commands (file):")
        self.commands_file_entry = ttk.Entry(self.root)
        self.commands_file_button = ttk.Button(self.root, text="Browse", command=self.browse_commands_file)
        self.commands_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.commands_file_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.commands_file_button.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Log
        self.log_text = tk.Text(self.root, height=10, width=50, state=tk.DISABLED)
        self.log_text.grid(row=5, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # Status
        self.status_label = ttk.Label(self.root, text="Status:")
        self.status_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")

        # Run Button
        self.run_button = ttk.Button(self.root, text="Run", command=self.run_config)
        self.run_button.grid(row=6, column=1, columnspan=2, padx=5, pady=5, sticky="w")

    def browse_ip_file(self):
        filename = filedialog.askopenfilename()
        self.ip_file_entry.delete(0, tk.END)
        self.ip_file_entry.insert(0, filename)

    def browse_commands_file(self):
        filename = filedialog.askopenfilename()
        self.commands_file_entry.delete(0, tk.END)
        self.commands_file_entry.insert(0, filename)

    def run_config(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        ssh_key = self.ssh_key_entry.get()
        ip_filename = self.ip_file_entry.get()
        commands_filename = self.commands_file_entry.get()

        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)

        logging.basicConfig(filename='log.txt', level=logging.INFO)

        def process_device(ip):
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                
                if ssh_key:
                    private_key = paramiko.RSAKey(filename=ssh_key)
                    client.connect(ip, username=username, pkey=private_key)
                else:
                    client.connect(ip, username=username, password=password)

                with open(commands_filename, 'r') as commands_file:
                    commands = commands_file.readlines()
                    for command in commands:
                        stdin, stdout, stderr = client.exec_command(command)
                        logging.info(f"Device {ip}: {command.strip()} - Success")

                client.close()
                self.log_text.insert(tk.END, f"Device {ip}: Configuration successful\n")
            except Exception as e:
                logging.error(f"Device {ip}: {str(e)}")
                self.log_text.insert(tk.END, f"Device {ip}: Configuration failed - {str(e)}\n")

        with open(ip_filename, 'r') as ip_file:
            ip_addresses = ip_file.readlines()

        threads = []
        for ip in ip_addresses:
            ip = ip.strip()
            thread = threading.Thread(target=process_device, args=(ip,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.log_text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkConfiguratorGUI(root)
    root.mainloop()
