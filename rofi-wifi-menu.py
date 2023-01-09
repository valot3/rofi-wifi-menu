#!/usr/bin/python3

# ------------------------------
# Imports
import os
import subprocess
import re
# ------------------------------



# ------------------------------
# List of connected Wi-Fi network interfaces
command = 'nmcli --fields "DEVICE,TYPE" device status | grep "wifi" | grep -v "p2p" | cut -d " " -f 1'
wifi_network_interfaces = os.popen(command).read().split("\n")
wifi_network_interfaces.remove("")

# ------------------------------
# Generate a list of all available Wi-Fi AP's for each interface
wifi_ap_list=""
for interface in wifi_network_interfaces:
    command = 'nmcli --fields "SECURITY,SSID,BARS,SIGNAL" device wifi list ifname ' + interface + ' --rescan yes | sed 1d | sed "s/  */ /g" | sed -E "s/WPA*.?\S//g" | sed "s/^--//g" | sed "s/ //g" | sed "/--/d" | awk -F " ▂" \'{print $1"~~~""▂"$2}\''
    command_output = os.popen(command).read()
    

    wifi_ap_list = wifi_ap_list + "\n" + interface + ":\n"
    
    # Adding the interface name to each line of info about the AP
    tmp_wifi_ap_list = ""

    ap_list = command_output.split("\n")
    ap_list.remove("") # Remove empty value
    for ap in ap_list:
        ap = ap.split("~~~")
        ap.insert(1, "~~~[{}]***".format(interface))
        final_ap = " ".join(ap)
        tmp_wifi_ap_list += final_ap + "\n"

    # Make AP list prettier
    command = 'echo -e "{}" | column -t -s "~~~" -o "       " | column -t -s "***" -o ""'.format(tmp_wifi_ap_list)
    command_output = os.popen(command).read()    
    wifi_ap_list += command_output

# ------------------------------
# Set enable/disable option
command = 'nmcli -fields WIFI g | sed 1d'
connected = os.popen(command).read()

if "enabled" in connected:
    option = "睊 Disable Wi-Fi" 
elif "disabled" in connected:
    option = "直 Enable Wi-Fi"
else:
    option = "[!] Error: Unknown Wi-Fi status"

# ------------------------------
# Use rofi to select wifi network/option
command = 'echo -e "{}\n{}" | uniq -u | rofi -dmenu -i -select-row 1 -p "Wi-Fi SSID"'.format(option,wifi_ap_list)
chosen_network = os.popen(command).read()
if chosen_network in ["\n", " ", "", None]: # Prevent bug
    quit()

chosen_option = chosen_network.split(" ")[1]

# ------------------------------
# Run selected option
if chosen_option in wifi_network_interfaces:
    quit()

elif chosen_option == "直 Enable Wi-Fi":
    command = "nmcli radio wifi on"
    command = command.split(" ")
    subprocess.run(command)

elif chosen_option == "睊 Disable Wi-Fi":
    command = "nmcli radio wifi off"
    command = command.split(" ")
    subprocess.run(command)

else:
    interface = str(re.search("\[.*\]", chosen_network).group())
    interface = interface.replace("[", "")
    interface = interface.replace("]", "")

    # If it is a saved connection...
    saved_connections = os.popen("nmcli -g NAME connection").read()
    if chosen_option in saved_connections:
        command = "nmcli device wifi connect \"{}\" ifname \"{}\"".format(chosen_option, interface)
        command = command.split(" ")
        command_output = subprocess.run(command, text=True, capture_output=True).stdout
        if "successfully" in command_output:
            pass
        else:
            command = 'notify-send "Error during connection"'
            command = command.split(" ")
            subprocess.run(command)
    
    # If is a new connection...
    elif "" in chosen_network:
        command = 'rofi -dmenu -p "Password"'
        wifi_password = os.popen(command).read()

        command = "nmcli device wifi connect \"{}\" password \"{}\"".format(chosen_option, wifi_password)
        command = command.split(" ")
        command_output = subprocess.run(command, text=True, capture_output=True).stdout
        if "successfully" in command_output:
            pass
        else:
            command = 'notify-send "Error during connection"'
            command = command.split(" ")
            subprocess.run(command)

    elif "" in chosen_network:
        command = "nmcli device wifi connect \"{}\"".format(chosen_option)
        command = command.split(" ")
        command_output = subprocess.run(command, text=True, capture_output=True).stdout
        if "successfully" in command_output:
            pass
        else:
            command = 'notify-send "Error during connection"'
            command = command.split(" ")
            subprocess.run(command)

# ------------------------------
