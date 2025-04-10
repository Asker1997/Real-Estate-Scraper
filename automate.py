import subprocess
import datetime
import sys
import os

#This script is to automate adding tasks to task scheduler in windows where final_vip.py runs for every given website below in "sites" 
# With the characteristics that runtime is at 18:00 and it will run every 12 hours indefinitely. 

#The update_sold.py script is also added to tasks



#The 9 most important streets/districts in the capital of Azerbaijan for real estate activity.
sites = ['https://bina.az/baki/fontanlar-bagi/alqi-satqi/obyektler',
         'https://bina.az/baki/xalqlar-dostlugu/alqi-satqi/obyektler',
         'https://bina.az/baki/neftciler/alqi-satqi/obyektler',
         'https://bina.az/baki/memar-ecemi/alqi-satqi/obyektler',
         'https://bina.az/baki/ehmedli/alqi-satqi/obyektler',
         "https://bina.az/baki/semed-vurgun-parki/alqi-satqi/obyektler?items_view=list",
         "https://bina.az/baki/port-baku/alqi-satqi/obyektler",
         "https://bina.az/baki/iceri-seher/alqi-satqi/obyektler",
         "https://bina.az/baki/28-may/alqi-satqi/obyektler",
         ]


python_path = sys.executable

#To get absolute path of the current directory for windows task-scheduler. Can't use relative path. 
folder_path = os.getcwd()
script_name = "final_vip.py"

task_runtime = "18:00"
task_date = datetime.datetime.now().strftime("%d/%m/%Y")


#This is to schedule the 9 website tasks for final_vip.py
for site in sites:

    parts = site.split('/')

    task_name = parts[4]

    cmd = (f' cmd.exe /c cd /d \"{folder_path}\" && ' 
       f'\"{python_path}\" \"{script_name}\" {site}"')
    
    command = [
    "schtasks",
    "/create",
    "/f",
    "/tn", task_name,
    "/tr", cmd,
    "/sc", "DAILY",
    "/st", task_runtime,
    "/sd", task_date,
    "/ri", "720",
    "/du", "9999:00"
]
    
    try:
        subprocess.run(command, check=True)
        print("Task created successfully!")
    except subprocess.CalledProcessError as e:
        print("An error occurred:", e)
    



#This is to schedule the update_sold.py task
cmd_update_sold = (f' cmd.exe /c cd /d \"{folder_path}\" && ' 
    f'\"{python_path}\" \"update_sold.py\" ')


command_update_sold = [
    "schtasks",
    "/create",
    "/f",
    "/tn", "Update_Sold",
    "/tr", cmd_update_sold,
    "/sc", "DAILY",
    "/st", "18:20",
    "/sd", task_date,
    "/ri", "720",
    "/du", "9999:00"
]

try:
    subprocess.run(command_update_sold, check=True)
    print("Task created successfully!")
except subprocess.CalledProcessError as e:
        print("An error occurred:", e)