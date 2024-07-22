import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

def create_config_file(data):
    hostname = data['hostname'].get()
    ip_domain_name = data['ip_domain_name'].get()
    enable_password = data['enable_password'].get()
    admin_username = data['admin_username'].get()
    admin_password = data['admin_password'].get()
    interface_range = data['interface_range'].get()
    uplink_interface = data['uplink_interface'].get()
    access_vlan = data['access_vlan'].get()
    access_mode = data['access_mode'].get()
    management_interface = data['management_interface'].get()
    management_ip_address = data['management_ip_address'].get()
    management_netmask = data['management_netmask'].get()
    voice_vlan = data['voice_vlan'].get()
    ip_route = data['ip_route'].get()
    ip_default_gateway = data['ip_default_gateway'].get()
    line_console_password = data['line_console_password'].get()
    additional_vlans = data['additional_vlans'].get().split(',')

    vlan_numbers = range(10, 1000, 10)

    config = f"""
hostname {hostname}
ip domain name {ip_domain_name}
crypto key generate rsa
 2048
!
no aaa new-model
enable password {enable_password}
!
username {admin_username} password {admin_password}
no aaa new-model
!
!
vlan internal allocation policy ascending
!
lldp run
!
no ip http server
no ip http authentication local
no ip http secure-server
!
interface {uplink_interface}
switchport mode trunk
description UPLINK
!
interface range {interface_range}
 switchport {access_mode} vlan {access_vlan}
 switchport mode access
"""

    if voice_vlan:
        config += f" switchport voice vlan {voice_vlan}\n"

    config += "!\n"

    if management_interface:
        config += f"""
interface vlan{management_interface}
 description MANAGEMENT
 ip address {management_ip_address} {management_netmask}
 no shutdown
"""
    else:
        config += """
interface vlan 1
 no ip address
 shutdown
"""

    config += f"""
ip route {ip_route}
ip default-gateway {ip_default_gateway}
ip ssh time-out 120
ip ssh authentication-retries 5
ip ssh version 2
!
line con 0
 password {line_console_password}
line vty 0 15
 transport input ssh
line vty 11 15
"""

    for vlan_number, vlan_name in zip(vlan_numbers, additional_vlans):
        config += f"!\nvlan {vlan_number}\n name {vlan_name}\n no shutdown\n"

    config += """
!
!
service password-encryption
aaa new-model
aaa authentication login default local
do wr mem
end

"""

    file_name = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if file_name:
        with open(file_name, "w") as file:
            file.write(config)
        messagebox.showinfo("Success", "Yapılandırma dosyası başarıyla kaydedildi.")
    else:
        messagebox.showwarning("Canceled", "Dosya kaydetme işlemi iptal edildi.")

def main():
    root = tk.Tk()
    root.title("Cisco Configuration Generator")

    data = {
        'hostname': tk.StringVar(),
        'ip_domain_name': tk.StringVar(),
        'enable_password': tk.StringVar(),
        'admin_username': tk.StringVar(),
        'admin_password': tk.StringVar(),
        'interface_range': tk.StringVar(),
        'uplink_interface': tk.StringVar(),
        'access_vlan': tk.StringVar(),
        'access_mode': tk.StringVar(),
        'management_interface': tk.StringVar(),
        'management_ip_address': tk.StringVar(),
        'management_netmask': tk.StringVar(),
        'voice_vlan': tk.StringVar(),
        'ip_route': tk.StringVar(),
        'ip_default_gateway': tk.StringVar(),
        'line_console_password': tk.StringVar(),
        'additional_vlans': tk.StringVar(),
    }

    # Form Layout
    fields = [
        ("Hostname", 'hostname'),
        ("IP Domain Name", 'ip_domain_name'),
        ("Enable Password", 'enable_password'),
        ("Admin Username", 'admin_username'),
        ("Admin Password", 'admin_password'),
        ("Interface Range (e.g. GigabitEthernet1/0/1-2)", 'interface_range'),
        ("Uplink Interface (e.g. GigabitEthernet1/0/1 veya TenGigabitEthernet1/0/1)", 'uplink_interface'),
        ("Access VLAN", 'access_vlan'),
        ("Access Mode (e.g. access/trunk)", 'access_mode'),
        ("Management vlan Interface (e.g. Vlan10 (press enter if none))", 'management_interface'),
        ("Management IP Adress (e.g. 192.168.10.2 (press enter if none))", 'management_ip_address'),
        ("Management Netmask (e.g. 255.255.255.0)", 'management_netmask'),
        ("Voice VLAN (press enter if none)", 'voice_vlan'),
        ("IP Route e.g A.B.C.D A.B.C.D A.B.C.D:", 'ip_route'),
        ("IP Default Gateway", 'ip_default_gateway'),
        ("Console Line Password", 'line_console_password'),
        ("Additional VLANs (comma-separated)", 'additional_vlans'),
    ]

    for idx, (label, key) in enumerate(fields):
        tk.Label(root, text=label, anchor='w').grid(row=idx, column=0, padx=10, pady=5, sticky='w')
        tk.Entry(root, textvariable=data[key]).grid(row=idx, column=1, padx=10, pady=5, sticky='w')

    # Submit button
    tk.Button(root, text="Generate Config", command=lambda: create_config_file(data)).grid(row=len(fields), columnspan=2, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
