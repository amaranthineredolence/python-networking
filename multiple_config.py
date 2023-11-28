import netmiko
from netmiko import  ConnectHandler
import subprocess

def Username():
    Posistion_Counter = 0
    Result = subprocess.getoutput("whoami")
    for words in Result:
        if words =="\\":
            Position = Posistion_Counter
            break
        Posistion_Counter +=1
    return Result[Position + 1: ]

Local_computer_Username = Username()

List_of_Switches = []
Number_of_Switches = int(input("how many switches? : "))

for switch in range(1,Number_of_Switches +1) :
    Ask = input("Enter switch number " + str(switch) + ":")
    List_of_Switches.append(Ask)            

User = input("What is user: ")
Pass = input("What is PSWD: ")

for switches in List_of_Switches:

    Network_Device = {"host": switches,
                  "username": User,
                  "password": Pass,
                  "device_type": "cisco_ios"
                  }

Connect_to_Device = ConnectHandler(**Network_Device)

Connect_to_Device.enable()

Lst_of_Commands = ["show run | i hostname",
                    "show ver",
                    ]

for command in Lst_of_Commands:
    output = Connect_to_Device.send_command(command)

    with open("C:\\Users\\" +Local_computer_Username+ "\\Desktop\\scrpt\\config_test.text","a") as f:
        f.write("\n")
        f.write(switches + "#" + command)
        f.write("\n")
        f.write(Connect_to_Device.send_command(command))
        f.write("\n")
    with open("C:\\Users\\" +Local_computer_Username+ "\\Desktop\\scrpt\\config_test.text","a") as f:
        f.write(switches + "#")
        f.write("\n"*3)
        f.write("\nEND of this device/END of this device/END of this device"*4)
        f.write("\n"*3)

print("\nComplete")
