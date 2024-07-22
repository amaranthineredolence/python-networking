import tkinter as tk
from tkinter import filedialog

class ConfigGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cisco Config Generator")

        self.vlan_entries = []
        self.ip_entries = []
        self.mask_entries = []
        self.priority_entries = []
        self.hsrp_ip_entries = []

        self.create_widgets()

    def create_widgets(self):
        # Header labels
        tk.Label(self.root, text="VLAN ID").grid(row=0, column=0)
        tk.Label(self.root, text="IP Address").grid(row=0, column=1)
        tk.Label(self.root, text="Subnet Mask").grid(row=0, column=2)
        tk.Label(self.root, text="Priority").grid(row=0, column=3)
        tk.Label(self.root, text="HSRP IP").grid(row=0, column=4)

        # Add initial row
        self.add_row()

        # Add row button
        add_row_button = tk.Button(self.root, text="Add Row", command=self.add_row)
        add_row_button.grid(row=1, column=5)

        # Generate config button
        generate_button = tk.Button(self.root, text="Generate Config", command=self.generate_config)
        generate_button.grid(row=2, column=5)

        # Output label
        self.output_label = tk.Label(self.root, text="")
        self.output_label.grid(row=3, column=0, columnspan=6)

    def add_row(self):
        row = len(self.vlan_entries) + 1

        vlan_entry = tk.Entry(self.root)
        vlan_entry.grid(row=row, column=0)
        self.vlan_entries.append(vlan_entry)

        ip_entry = tk.Entry(self.root)
        ip_entry.grid(row=row, column=1)
        self.ip_entries.append(ip_entry)

        mask_entry = tk.Entry(self.root)
        mask_entry.grid(row=row, column=2)
        self.mask_entries.append(mask_entry)

        priority_entry = tk.Entry(self.root)
        priority_entry.grid(row=row, column=3)
        self.priority_entries.append(priority_entry)

        hsrp_ip_entry = tk.Entry(self.root)
        hsrp_ip_entry.grid(row=row, column=4)
        self.hsrp_ip_entries.append(hsrp_ip_entry)

    def generate_config(self):
        config_text = ""

        for vlan_entry, ip_entry, mask_entry, priority_entry, hsrp_ip_entry in zip(
                self.vlan_entries, self.ip_entries, self.mask_entries, self.priority_entries, self.hsrp_ip_entries):
            
            vlan_id = vlan_entry.get().strip()
            ip_address = ip_entry.get().strip()
            subnet_mask = mask_entry.get().strip()
            priority = priority_entry.get().strip()
            hsrp_ip = hsrp_ip_entry.get().strip()

            if vlan_id and ip_address and subnet_mask and priority and hsrp_ip:
                config_text += f"""interface Vlan{vlan_id}
  no shutdown
  no ip redirects
  ip address {ip_address}/{subnet_mask}
  hsrp {vlan_id}
    preempt
    priority {priority}
    ip {hsrp_ip}
"""

        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(config_text)
            self.output_label.config(text=f"Configuration saved to {file_path}")
        else:
            self.output_label.config(text="Save cancelled")

# GUI'yi oluştur ve çalıştır
root = tk.Tk()
app = ConfigGeneratorApp(root)
root.mainloop()
