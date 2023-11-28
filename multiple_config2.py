
import subprocess, re, time, netmiko
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from netmiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException
from netmiko import SCPConn
from datetime import datetime
#Important parameters that can be changed and controlled from here#
ip_list = ['192.168.1.179', '192.168.1.178']
#Cisco IOS 2801 Data
new_ios_2801 = "c2801-ipvoice_ivs-mz.150-1.M7.bin"
new_ios_2801_size = "41735808"
new_ios_2801_md5 = "66c50292167f2b1c1ccd9ead3d5a5db4"
#Cisco IOS 2811 Data
new_ios_2811 = "c2800nm-ipvoice_ivs-mz.151-2.T1.bin"
new_ios_2811_size = "51707860"
new_ios_2811_md5 = "bf3e0811b5626534fd2e4b68cdd042df"
copy_from = "tftp"
copy_to = "flash:"
tftp_ip = "192.168.1.100"
reload_wait_time = "300"
auto_copy_to_flash = "Yes"
auto_change_boot_sequence ="Yes"
auto_reload = "Yes"
#########################################
#Creating the CSV files for pre and post upgrade#
#clearing the old data from the CSV file and writing the headers
f = open("pre_upgrade.csv", "w+")
f.write("IP Address, Hostname, Uptime, Current_Version, Current_Image, Serial_Number, Device_Model, Device_Memory")
f.write("\n")
f.close()
#clearing the old data from the CSV file and writing the headers
f = open("post_upgrade.csv", "w+")
f.write("IP Address, Hostname, Uptime, Current_Version, Current_Image, Serial_Number, Device_Model, Device_Memory")
f.write("\n")
f.close()
#clearing the old data from the logs file and writing the headers
f = open("logs.txt", "w+")
f.close()
now = datetime.now()
logs_time = now.strftime("%H:%M:%S")
#############################################################################################################################
def preupgrade():
    
    for ip in ip_list:
        cisco = {
        'device_type':'cisco_ios_telnet',
        'ip':ip,
        'username':'cisco',     #ssh username
        'password':'cisco',  #ssh password
        'secret': 'cisco',   #ssh_enable_password
        'ssh_strict':False,  
        'fast_cli':False,
        }
        
        now = datetime.now()
        logs_time = now.strftime("%H:%M:%S")
        print("" + logs_time + ": " + ip  + " Checking this device, Collecting pre-report ")
        #handling exceptions errors
        
        try:
            net_connect = ConnectHandler(**cisco)
        
        except (NetMikoTimeoutException, AuthenticationException, SSHException, ValueError, TimeoutError, ConnectionError, ConnectionResetError, OSError):
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " device login issue " + "\n" )
            f.close()
            continue
        try:
            net_connect.enable()
        
        #handling exceptions errors        
        except (NetMikoTimeoutException, AuthenticationException, SSHException, ValueError, TimeoutError, ConnectionError, ConnectionResetError):
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " device login issue " + "\n" )
            f.close()
            continue
        
        #list where informations will be stored
        pre_upgrade_devices = []
                
        # execute show version on router and save output to output object    
        sh_ver_output = net_connect.send_command('show version')   
        #finding hostname in output using regular expressions
        regex_hostname = re.compile(r'(\S+)\suptime')
        hostname = regex_hostname.findall(sh_ver_output)
        #finding uptime in output using regular expressions
        regex_uptime = re.compile(r'\S+\suptime\sis\s(.+)')
        uptime = regex_uptime.findall(sh_ver_output)
        uptime = str(uptime).replace(',' ,'').replace("'" ,"")
        uptime = str(uptime)[1:-1] 
        
        
        #finding version in output using regular expressions
        regex_version = re.compile(r'Cisco\sIOS\sSoftware.+Version\s([^,]+)')
        version = regex_version.findall(sh_ver_output)
        #finding serial in output using regular expressions
        regex_serial = re.compile(r'Processor\sboard\sID\s(\S+)')
        serial = regex_serial.findall(sh_ver_output)
        #finding ios image in output using regular expressions
        regex_ios = re.compile(r'System\simage\sfile\sis\s"([^ "]+)')
        ios = regex_ios.findall(sh_ver_output)
        #finding model in output using regular expressions
        regex_model = re.compile(r'[Cc]isco\s(\S+).*memory.')
        model = regex_model.findall(sh_ver_output)
        
        #finding the router's memory using regular expressions
        regex_memory = re.search(r'with (.*?) bytes of memory', sh_ver_output).group(1)
        memory = regex_memory
        
        
        
        #append results to table [hostname,uptime,version,serial,ios,model]
        pre_upgrade_devices.append([ip, hostname[0],uptime,version[0],ios[0], serial[0],model[0], memory])
        
        
        #print all results (for all routers) on screen    
        for i in pre_upgrade_devices:
            i = ", ".join(i)      
            f = open("pre_upgrade.csv", "a")
            f.write(i)
            f.write("\n")
            f.close()    
            
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
    
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " collecting pre upgrade report " + "\n" )
            f.close()
        
            #If Auto Copy to flash is enabled - Then start copying the files to Flash#                
        if auto_copy_to_flash == "Yes":
            #print("Checking Auto Copy to Flash as Yes")
            
        
            #Check necessary space on Flash:#    
            output = net_connect.send_command('show flash')
            output = re.findall(r"\w+(?= bytes available)", output)
            output = ", ".join(output)
            if model[0] == "2801":        
                check_if_space_available = int(output) - int(new_ios_2801_size)
                #print(str(check_if_space_available))
                
                if int(check_if_space_available) > 0 :
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " Sufficient space available ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " Sufficent space available" + "\n" )
                    f.close()
                    time.sleep(2)
                    pass
                    
                elif int(check_if_space_available) < 0: now = datetime.now() logs_time = now.strftime("%H:%M:%S") print("" + logs_time + ": " + ip + " Not enough space ") f = open("logs.txt", "a") f.write("" + logs_time + ": " + ip + " not enough space" + "\n" ) f.close() continue if model[0] == "2811": check_if_space_available = int(output) - int(new_ios_2811_size) #print(str(check_if_space_available)) if int(check_if_space_available) > 0 :
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " Sufficient space available ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " Sufficent space available" + "\n" )
                    f.close()
                    time.sleep(2)
                    pass
                    
                elif int(check_if_space_available) < 0:    
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " Not enough space ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " not enough space" + "\n" )
                    f.close()
                    continue
                    
            #Copy TFTP to FLASH#
            command = "copy " + copy_from + " " + copy_to
            start_time = datetime.now()
            output = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=1)
            
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            print("" + logs_time + ": " + ip  + " " + output)
            #print(output)
            
            #Entering the TFTP IP Address#
            command = tftp_ip
            start_time = datetime.now()
            #output = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=2)
            output = net_connect.send_command(command, expect_string=r']?')
            
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            print("" + logs_time + ": " + ip  + " " + output)
                
            
            #If the router model is 2801 - Run this code#
            if model[0] == "2801":            
                command = new_ios_2801
                start_time = datetime.now()
                #output = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=1)
                output = net_connect.send_command(command, expect_string=r']?')
                now = datetime.now()
                logs_time = now.strftime("%H:%M:%S")
                print("" + logs_time + ": " + ip  + " " + output)
                
                command = new_ios_2801
                start_time = datetime.now()
                #net_connect.send_config_set(config_commands)
                output = net_connect.send_command_timing(command, delay_factor=10, strip_prompt=False, strip_command=False)
                now = datetime.now()
                logs_time = now.strftime("%H:%M:%S")
                print("" + logs_time + ": " + ip  + " " + output)
                                    
                if re.search(r'\sbytes copied\b',output):
                        
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " File copied successfully ")    
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " file copied successfully" + "\n" )
                    f.close()
                    
                    
                    
                    command = "verify /md5 flash:" + new_ios_2801
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    #output = net_connect.send_command(command, expect_string=r']?')
                    output = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=5)
                    print("" + logs_time + ": " + ip  + "Calculated MD5 is : " + output + "\n" "Expected MD5 is : " + new_ios_2801_md5 )
                    try:
                        output = re.search(' = (\w+)',output)
                        print(output)    
                        
                    except AttributeError:
                        output = re.search(' = (\w+)',output), output.group(1)
                        #print(output.group(1))    
                    
                    if new_ios_2801_md5 == str(output.group(1)):
                        
                        now = datetime.now()
                        logs_time = now.strftime("%H:%M:%S")
                        print("" + logs_time + ": " + ip  + " MD5 checksum verified ")
                        
                        f = open("logs.txt", "a")
                        f.write("" + logs_time + ": " + ip  + " MD5 checksum verified" + "\n" )
                        f.close()
                        
                        
                        
                                            
                    elif new_ios_2801_md5 != str(output.group(1)):
                        now = datetime.now()
                        logs_time = now.strftime("%H:%M:%S")
                        print("" + logs_time + ": " + ip  + " MD5 checksum mismatch ")
                
                        f = open("logs.txt", "a")
                        f.write("" + logs_time + ": " + ip  + " MD5 checksum mismatch" + "\n" )
                        f.close()                    
                        
                        continue
                
                                
                
                elif re.search(r'\%Error copying\b',output):
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " Error copying the file ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " error copying file" + "\n" )
                    f.close()
                    continue
                    
                elif re.search(r'\%Error opening\b',output):
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " File does not exist ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " file does not exist" + "\n" )
                    f.close()
                    continue
                    
                elif re.search(r'\bAccessing',output):
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " Please check your TFTP/SCP service/network network connectivity ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " check your TFTP/SCP service/network network connectivity" + "\n" )
                    f.close()                
                    continue
                    
                    
        
            
            #If the router model is 2811 - Run this code#
            elif model[0] == "2811":            
                command = new_ios_2811
                start_time = datetime.now()
                #output = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=1)
                output = net_connect.send_command(command, expect_string=r']?')
                now = datetime.now()
                logs_time = now.strftime("%H:%M:%S")
                print("" + logs_time + ": " + ip  + " " + output)
                
                command = new_ios_2811
                start_time = datetime.now()
                #net_connect.send_config_set(config_commands)
                output = net_connect.send_command_timing(command, delay_factor=10, strip_prompt=False, strip_command=False)
                now = datetime.now()
                logs_time = now.strftime("%H:%M:%S")
                print("" + logs_time + ": " + ip  + " " + output)
                                    
                if re.search(r'\sbytes copied\b',output):
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " File copied successfully ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " file copied successfully" + "\n" )
                    f.close()
                    
                    
                    command = "verify /md5 flash:" + new_ios_2811
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    #output = net_connect.send_command(command, expect_string=r']?')
                    output = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=5)
                    print("" + logs_time + ": " + ip  + "Calculated MD5 is : " + output + "\n" "Expected MD5 is : " + new_ios_2811_md5 )
                    #print(output)
                    try:
                        output = re.search(' = (\w+)',output)
                        #print(output)    
                        
                    except AttributeError:
                        output = re.search(' = (\w+)',output), output.group(1)
                        #print(output.group(1))    
                    
                    if new_ios_2811_md5 == str(output.group(1)):
                        now = datetime.now()
                        logs_time = now.strftime("%H:%M:%S")
                        print("" + logs_time + ": " + ip  + " MD5 checksum successfully matched ")
                        
                        f = open("logs.txt", "a")
                        f.write("" + logs_time + ": " + ip  + " MD5 checksum verified" + "\n" )
                        f.close()
                        
                                            
                    elif new_ios_2811_md5 != str(output.group(1)):
                        now = datetime.now()
                        logs_time = now.strftime("%H:%M:%S")
                        print("" + logs_time + ": " + ip  + " MD5 checksum mismatch ")
                    
                        f = open("logs.txt", "a")
                        f.write("" + logs_time + ": " + ip  + " MD5 checksum mismatch" + "\n" )
                        f.close()                    
                        continue
                    
                                
                
                elif re.search(r'\%Error copying\b',output):
                        
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " Error copying the file ")    
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " error copying file" + "\n" )
                    f.close()
                    continue
                    
                elif re.search(r'\%Error opening\b',output):
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " File does not exist ")    
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " file does not exist" + "\n" )
                    f.close()    
                    continue    
                    
                elif re.search(r'\bAccessing',output):
                    now = datetime.now()
                    logs_time = now.strftime("%H:%M:%S")
                    print("" + logs_time + ": " + ip  + " Please check your TFTP/SCP service/network network connectivity ")
                    f = open("logs.txt", "a")
                    f.write("" + logs_time + ": " + ip  + " check your TFTP/SCP service/network network connectivity" + "\n" )
                    f.close()                
                    continue        
                    
                    
                            
                    
            #If Auto Copy to flash is disabled - Then continue to next step#        
        elif auto_copy_to_flash == "No":
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            print("" + logs_time + ": " + ip  + " Auto copy to flash is set as No ")
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " Auto copy to flash is set as No " + "\n" )
            f.close()
            pass                
                        
        if auto_change_boot_sequence == "Yes":        
        
            #Enter the New IOS#
            output = net_connect.send_command('show version') 
            regex_ios = re.compile(r'System\simage\sfile\sis\s"([^ "]+)')
            current_ios = regex_ios.findall(output)
            current_ios = ", ".join(current_ios)
            
            remove_boot = "no boot system"
            remove_boot = net_connect.send_config_set(remove_boot)
            
            if model[0] == "2801":
                add_boot1 = "boot system flash:" + new_ios_2801
                add_boot1 = net_connect.send_config_set(add_boot1)
                
            elif model[0] == "2811":
                add_boot1 = "boot system flash:" + new_ios_2811
                add_boot1 = net_connect.send_config_set(add_boot1)
                
            
            add_boot2 =  "boot system " + str(current_ios)
            add_boot2 = net_connect.send_config_set(add_boot2)
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            print("" + logs_time + ": " + ip  + " Boot sequence changed ")
            
            #write_config = net_connect.send_command('wr mem', expect_string='[OK]')
            command = "wr mem"
            write_config = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=2)
            
            command = ""
            write_config = net_connect.send_command_timing(command, strip_prompt=False, strip_command=False, delay_factor=2)
            
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            print("" + logs_time + ": " + ip  + " Configuration saved ")
            
            
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " configuration saved" + "\n" )
            f.close()
                        
        elif auto_change_boot_sequence == "No":
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            print("" + logs_time + ": " + ip  + " Please change the boot sequence manually! and proceed with reload ")
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " Please change the boot sequence manually! and proceed with reload" + "\n" )
            f.close()
            pass
                
        if auto_reload == "Yes":
        
            try:
                
                confirm_reload = net_connect.send_command('reload', expect_string='[confirm]')
                confirm_reload = net_connect.send_command('\n', expect_string='[confirm]')
                now = datetime.now()
                logs_time = now.strftime("%H:%M:%S")
                
                f = open("logs.txt", "a")
                f.write("" + logs_time + ": " + ip  + " Reload command sent" + "\n" )
                f.close()
                
                print("" + logs_time + ": " + ip  + " Sending reload command ")
            except Exception as e:
                print(e)
                f = open("logs.txt", "a")
                f.write("" + logs_time + ": " + ip  + " Reload command sent" + "\n" )
                f.close()
                
                print("" + logs_time + ": " + ip  + " Sending reload command ")
        elif auto_reload== "No":
            
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            print("" + logs_time + ": " + ip  + " Please reload the router manually ")
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " Please reload the router manually" + "\n" )
            f.close()
            pass
                    
                    
                        
preupgrade()
def sleeptime():
    now = datetime.now()
    logs_time = now.strftime("%H:%M:%S")
    print("" + logs_time + ": Wait time activated, please wait for " + str(reload_wait_time) + " seconds")
    time.sleep(int(reload_wait_time))
sleeptime()    
                    
def    postupgrade():
    
    for ip in ip_list:
        cisco = {
        'device_type':'cisco_ios_telnet',
        'ip':ip,
        'username':'cisco',     #ssh username
        'password':'cisco',  #ssh password
        'secret': 'cisco',   #ssh_enable_password
        'ssh_strict':False,  
        'fast_cli':False,
        }
    
        now = datetime.now()
        logs_time = now.strftime("%H:%M:%S")
        print("" + logs_time + ": " + ip  + " Checking this device, Collecting post-report ")
                    
        try:
            #time.sleep(int(reload_wait_time))
            net_connect = ConnectHandler(**cisco)
        except (NetMikoTimeoutException, AuthenticationException, SSHException, ValueError, TimeoutError, ConnectionError, ConnectionResetError):
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " device login issue " + "\n" )
            f.close()
            continue
        try:
            net_connect.enable()
            
        #handling exceptions errors        
        except (NetMikoTimeoutException, AuthenticationException, SSHException, ValueError, TimeoutError, ConnectionError, ConnectionResetError, OSError):
            now = datetime.now()
            logs_time = now.strftime("%H:%M:%S")
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " device login issue " + "\n" )
            f.close()
            continue
        
        #list where informations will be stored
        post_upgrade_devices = []
        
        # execute show version on router and save output to output object    
        sh_ver_output = net_connect.send_command('show version')   
        #finding hostname in output using regular expressions
        regex_hostname = re.compile(r'(\S+)\suptime')
        hostname = regex_hostname.findall(sh_ver_output)
        #finding uptime in output using regular expressions
        regex_uptime = re.compile(r'\S+\suptime\sis\s(.+)')
        uptime = regex_uptime.findall(sh_ver_output)
        uptime = str(uptime).replace(',' ,'').replace("'" ,"")
        uptime = str(uptime)[1:-1] 
        
        
        #finding version in output using regular expressions
        regex_version = re.compile(r'Cisco\sIOS\sSoftware.+Version\s([^,]+)')
        version = regex_version.findall(sh_ver_output)
        #finding serial in output using regular expressions
        regex_serial = re.compile(r'Processor\sboard\sID\s(\S+)')
        serial = regex_serial.findall(sh_ver_output)
        #finding ios image in output using regular expressions
        regex_ios = re.compile(r'System\simage\sfile\sis\s"([^ "]+)')
        ios = regex_ios.findall(sh_ver_output)
        #finding model in output using regular expressions
        regex_model = re.compile(r'[Cc]isco\s(\S+).*memory.')
        model = regex_model.findall(sh_ver_output)
        
        #finding the router's memory using regular expressions
        regex_memory = re.search(r'with (.*?) bytes of memory', sh_ver_output).group(1)
        memory = regex_memory
        
        
        
        #append results to table [hostname,uptime,version,serial,ios,model]
        post_upgrade_devices.append([ip, hostname[0],uptime,version[0],ios[0], serial[0],model[0], memory])
                
    #print all results (for all routers) on screen    
        for i in post_upgrade_devices:
            i = ", ".join(i)      
            f = open("post_upgrade.csv", "a")
            f.write(i)
            f.write("\n")
            f.close()
            f = open("logs.txt", "a")
            f.write("" + logs_time + ": " + ip  + " collecting post upgrade report " + "\n" )
            f.close()
postupgrade()
