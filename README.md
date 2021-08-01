#Disclaimer
This tool was made specifically for the use of my company and I will not take responsibility for anything that this tool may break or improperly configure for personal or professional reasons. Use this tool at your own risk.

See License

# Sonar v.2-Tik-Backup
This tool will create a .rsc file for all of your MikroTik devices that are assigned to a network site in Sonar v.2. It will also create a log file that shows the result for each attempt of pulling the backups.

# Prerequisites
A Sonar v.2 Instance
(Will not work with v.1, I do not have a v.1 instance to test any code against)

Python 3.7 or greater

Python Modules: paramiko, os, datetime, socket, pandas, gql

The machine that you run this on needs to be able to reach your network and your Sonar v.2 instance.

The MikroTik devices in Sonar v.2 need to be assigned to a network site, have an ip assignment with a description (I use the device name for the description), and a "deployment type".

# Setup
Line 12 --> Enter the top directory that you want the files to be created in.

Line 30 --> Enter your Sonar v.2 instance name.

Line 31 --> Eneter your really long Sonar v.2 token.

Line 35 --> Enter the username for your MikroTik devices.

Line 36 --> Enter the password for your MikroTik devices.

Line 137 --> Change "30" to the number of days worth of backups that you want to keep.

# Customization
I can customize this for you to use within your organization or I can create another custom tool for you.

If interested, reach out, you can find me on the WISP Talk Facebook group. - Chris Josey


