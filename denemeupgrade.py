import tkinter as tk
from tkinter import filedialog
import paramiko
import threading
import logging

class NetworkConfigurator:
    def __init__(self, master):
        self.master = master
        master.title("Network Device Configurator")

        self.username_label = tk.Label(master, text="Username:")
        self.username_label.grid(row=0, column=0)
        self.username_entry = tk.Entry(master)
        self.username_entry.grid(row=0, column=1)

        self.password_label = tk.Label(master, text="Password:")
        self.password_label.grid(row=1, column=0)
        self.password_entry = tk.Entry(master, show="*")
        self.password_entry.grid(row=1, column=1)

        self.key_label = tk.Label(master, text="SSH Key (optional):")
        self.key_label.grid(row=2, column=0)
        self.key_entry = tk.Entry(master)
        self.key_entry.grid(row=2, column=1)

        self.key_button = tk.Button(master, text="Browse", command=self.browse_ssh_key)
        self.key_button.grid(row=2, column=2)

        self.file_label = tk.Label(master, text="Devices and Commands File:")
        self.file_label.grid(row=3, column=0)
        self.file_entry = tk.Entry(master)
        self.file_entry.grid(row=3, column=1)

        self.file_button = tk.Button(master, text="Browse", command=self.browse_file)
        self.file_button.grid(row=3, column=2)

        self.run_button = tk.Button(master, text="Run Configuration", command=self.run_configuration)
        self.run_button.grid(row=4, column=1)

        # Set up logging
        logging.basicConfig(filename="configurator_log.txt", level=logging.INFO,
                            format="%(asctime)s - %(levelname)s - %(message)s")

    def browse_ssh_key(self):
        ssh_key_path = filedialog.askopenfilename(title="Select SSH Key File")
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, ssh_key_path)

    def browse_file(self):
        file_path = filedialog.askopenfilename(title="Select Devices and Commands File")
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, file_path)

    def run_configuration(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        ssh_key_path = self.key_entry.get()
        devices_file_path = self.file_entry.get()

        if not all([username, devices_file_path]):
            self.show_error("Username and Devices File are required.")
            return

        try:
            with open(devices_file_path, 'r') as file:
                devices_and_commands = [line.strip().split() for line in file.readlines()]

            for device_info in devices_and_commands:
                ip_address = device_info[0]
                commands = device_info[1:]

                try:
                    threading.Thread(target=self.configure_device, args=(ip_address, username, password, ssh_key_path, commands)).start()
                except Exception as e:
                    logging.error(f"Error while configuring device {ip_address}. Error: {str(e)}")

            logging.info("Configuration process started.")
        except Exception as e:
            logging.error(f"Failed to read devices and commands file. Error: {str(e)}")
            self.show_error("Failed to read devices and commands file.")

    def configure_device(self, ip_address, username, password, ssh_key_path, commands):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if ssh_key_path:
                private_key = paramiko.RSAKey(filename=ssh_key_path)
                ssh.connect(ip_address, username=username, pkey=private_key)
            else:
                ssh.connect(ip_address, username=username, password=password)

            for command in commands:
                stdin, stdout, stderr = ssh.exec_command(command)
                logging.info(f"Device {ip_address} - Command: {command} - Status: {stdout.channel.recv_exit_status()}")

            logging.info(f"Configuration completed for device {ip_address}")
        except Exception as e:
            logging.error(f"Failed to configure device {ip_address}. Error: {str(e)}")
        finally:
            if ssh:
                ssh.close()

    def show_error(self, message):
        error_window = tk.Toplevel(self.master)
        error_window.title("Error")
        error_label = tk.Label(error_window, text=message)
        error_label.pack()
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkConfigurator(root)
    root.mainloop()
