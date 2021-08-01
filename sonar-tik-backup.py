import paramiko, os, datetime, socket, pandas as pd
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

### Timestamp with time ###
dtimestamp = datetime.datetime.now().strftime("%b-%d-%Y_%H:%M:%S")

### Timestamp date only ###
timestamp = datetime.datetime.now().strftime("%m-%d-%Y_%H:%M:%S").split("_")[0]

### Main directory for files. Currently setup for linux machines ###
main_dir = "/home/scripts/Sonar-Tik-Backups"

### Sonar Class ###
class Sonar:
        def __init__(self, sonar_url, token):
            self.client = Client(
                transport=RequestsHTTPTransport(
                    url=sonar_url,
                    headers={
                        'Authorization': 'Bearer ' + token
                    }, timeout=1000
                )
            )

        def execute(self, query, variable_values):
            return self.client.execute(query, variable_values=variable_values)

### Your sonar Information ### 
url = 'https://YOURSONARINSTANCENAME.sonar.software/api/graphql'
token = 'YOURREALYLONGSONARTOKENYOURREALYLONGSONARTOKENYOURREALYLONGSONARTOKENYOURREALYLONGSONARTOKENYOURREALYLONGSONARTOKENYOURREALYLONGSONARTOKEN'
sonar = Sonar(url, token)

### Mikrotik credentials: Enter your username and password for your MikroTike devices ###
username = "YOURDEVICEUSERNAME"
password = "YOURDEVICEPASSWORD"

### Function to create log file item ###
def log_msg(msg):
    dev_log.append({"Timestamp":dtimestamp,
                    "Address":i['ip_assignments']['entities'][0]['ip_address'],
                    "Serial Number": srl_num,
                    "Model":model,
                    "Firmware":fw_ver,
                    "Device Name":i['ip_assignments']['entities'][0]['device_name'],
                    "Role":i['deployment_type']['deployment_type'],
                    "Backup":msg})
    
### Function to get Sonar network sites and site devices ###
def get_sonar():
    query = gql("""query network_sites($paginator: Paginator){
                network_sites(paginator: $paginator){
                    entities{
                    network_site:name
                    inventory_items{
                        entities{
                        deployment_type{
                        deployment_type:name
                        }
                        ip_assignments{
                            entities{
                            device_name:description
                            ip_address:subnet
                            }
                        }
                        inventory_model{
                            manufacturer{
                            manufacturer:name
                            }
                            model:name
                        }
                        }
                    }
                    }
                }
                }""")

    params = """{
    "paginator": {
        "page": 1,
        "records_per_page": 1000000
    }
    }"""
    GraphQL = sonar.execute(query=query, variable_values=params)
    return GraphQL

### List of dictionaries for log file ###
dev_log = []

### All Sonar network sites and site devices ###
devices = get_sonar()

### Loop to log into all Mikrotik devices and to get "compat" configuration ###
device_dict = []
for d in devices['network_sites']['entities']:
    srl_num = 'null'
    model = 'null'
    fw_ver = 'null'
    for i in d['inventory_items']['entities']:
        try:
            if i['inventory_model']['manufacturer']['manufacturer'] == "MikroTik":
                device_dict.append({"Network_Site": d['network_site'],
                                    "Deployment_Type": i['deployment_type']['deployment_type'],
                                    "Device_Description": i['ip_assignments']['entities'][0]['device_name'],
                                    "IP_Address": i['ip_assignments']['entities'][0]['ip_address'],
                                    "Make": i['inventory_model']['manufacturer']['manufacturer'],
                                    "Model": i['inventory_model']['model']})
                try:
                    host = i['ip_assignments']['entities'][0]['ip_address']
                    port = 22
                    command = "export compact"
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    ssh.connect(host, port, username, password, look_for_keys=False, timeout=2)
                    stdin, stdout, stderr = ssh.exec_command(command)
                    lines = stdout.readlines()
                    
                    ### Create sire directory if it doesnt exist ###
                    site_dir = f"{main_dir}/{d['network_site']}"
                    if not os.path.exists(site_dir):
                        os.makedirs(site_dir)
                    
                    ### Create role directory if it doesnt exist ###
                    role_dir = f"{site_dir}/{i['deployment_type']['deployment_type']}"
                    if not os.path.exists(role_dir):
                        os.makedirs(role_dir)
                    
                    ### Create device name directory if it doesnt exist ###
                    name_dir =f"{role_dir}/{i['ip_assignments']['entities'][0]['device_name']}"
                    if not os.path.exists(name_dir):
                        os.makedirs(name_dir)
                        
                    ### List of all the files in name_dir ###
                    dir_list = os.listdir(name_dir)
                    
                    ### Checks to see how many files are in name_dir and removes first file if there are >= 30 files ###
                    if len(dir_list) >= 30:
                        os.remove(f"{name_dir}/{dir_list[0]}")
                    
                    ### Creates .rsc files for each MikroTik device ###
                    with open(f"{name_dir}/{timestamp}-{i['ip_assignments']['entities'][0]['device_name']}.rsc","w") as file:
                        for l in lines:
                            if l.find("serial number") >= 0:
                                srl_num = l.split("=")[1].strip()
                            if l.find("model") >= 0:
                                model = l.split("=")[1].strip()
                            if l.find("RouterOS") >= 0:
                                fw_ver = l.split(" ")[-1].strip()
                            file.write(l)
                    log_msg("Successful")
                except TimeoutError:
                    log_msg("Timed Out")
                except socket.timeout:
                    log_msg("Timed Out")
                except socket.error:
                    log_msg("Socket Error")
                except TypeError:
                    log_msg("Missing Data")
                except:
                    log_msg("Unknown Error")
        except IndexError:
            pass             
       

### Creates backup_log.csv for all log_msg ###
df = pd.DataFrame(dev_log)
path = f"{main_dir}/backup_log.csv"
if os.path.exists(f"{main_dir}/backup_log.csv"):
    df.to_csv(path,mode="a",index=False,header=False)
else:
    df.to_csv(path,index=False)
