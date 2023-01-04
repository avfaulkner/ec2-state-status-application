import boto3
from datetime import datetime, timedelta, timezone, tzinfo
import csv 
import matplotlib.pyplot as plt
import pandas
import pytz
import random
import os
import json
import sys
import base64

# NOTE: 

# This script will query AWS for ec2 instances which have the slumbering-admin and t_role=admin tags and are in
# the running or stopped state. 
#
# This script will produce:
#  1. 2 csv files in the local directory with stopped and running admin vms.
#  2. a list of each admins' stopped/running status via stdout, can be piped into another file, etc
#  3. bar graphs that display each admins' stopped/running status
#
# To run this script locally, please install: 
#  pip install pandas matplotlib datetime boto3 pytz jupyter
#  export region=<region>
#  export AWS_PROFILE=<aws_profile>

# To view the graphs: 
#  **If running in wsl using vscode, pip install jupyter to view graph in interactive window, then 
#  right click the file or on the page containing the code if the file is open and select "Run current file in interactive window".

#  **If running the script in a terminal:
#  install xming (X11 for Windows, needed to view graphs from wsl terminal also) from sourcefourge or VcXsrv (xserver).
#  sudo apt-get install python3.8-tk
#  export DISPLAY=localhost:0.0 (can add to .bashrc to make permanent)


aws_profile = os.getenv('AWS_PROFILE')
# region = os.getenv('region')

# aws_profile = "cctqa"
region = "us-east-1"


boto3.setup_default_session(profile_name=aws_profile)
ec2 = boto3.client('ec2', region)
cloudtrail = boto3.client('cloudtrail')

datetime_format = '%Y-%m-%d %H:%M:%S'
today_date_utc = datetime.now(timezone.utc)
today_date_format = today_date_utc.strftime(datetime_format)
today_date_local = datetime.now().astimezone() # empty brackets = local timezone


msg_running=[]
msg_stopped=[]

instance_ids = []
instance_names = []
msg_running_str = []
msg_stopped_str = []

running_file = 'admins_running.csv'
stopped_file = 'admins_stopped.csv'



def main():
    # Use the filter() method of the instances collection to retrieve
    # all running and stopped Admin instances who have opted into the slumbering admin program. 
    filters = [
        {
            'Name': 'tag:t_role',
            'Values': ['Admin']
        },
        {
            'Name': 'instance-state-name', 
            'Values': ['running', 'stopped']
        },
        {
            'Name': 'tag:slumbering-admin', 
            'Values': ['true']  
        }
    ]
    msg_running=[]
    msg_stopped=[]
    reservations = ec2.describe_instances(Filters=filters).get('Reservations', [])
    for reservation in reservations:
        for instance in reservation['Instances']:
            tags = {}
            for tag in instance['Tags']:
                tags[tag['Key']] = tag['Value']
                if tag['Key'] == 'Name':
                    name=tag['Value']

                    if instance['State']['Name'] == 'running':
                        msg_running, running_stdout = running_admins(name, instance)
                    elif instance['State']['Name'] == 'stopped':
                        msg_stopped, stopped_stdout = stopped_admins(name, instance)
                    else:
                        pass # do nothing if instance state is not running or stopped. 
                    
    # running vm info
    if len(msg_running) > 0:
        write_running_csv(msg_running)
        print("Running Admins:\n",running_stdout)
        bar_graph_running(running_file)
    else:
        print('No running admins.\n')
    # stopped vm info
    if len(msg_stopped) > 0:
        write_stopped_csv(msg_stopped)   
        print("Stopped Admins:\n",stopped_stdout) 
        bar_graph_stopped(stopped_file)
    else:
        print('No stopped admins.')
        
    
def stopped_admins(name, instance):
    event = last_accessed(instance['InstanceId']).strftime(datetime_format)
    instance_ids.append(instance['InstanceId'])
    instance_names.append(name)
    stopped_reason = instance['StateTransitionReason'][16:35]
    stopped_time = stopped_reason if stopped_reason != '' else '1111-11-11 11:11:11'
    transition_timestamp = datetime.strptime(stopped_time, datetime_format)
    transition_timestamp_local = transition_timestamp.astimezone()  
    transition_timestamp_format = transition_timestamp_local.strftime(datetime_format)
    days = abs(today_date_local - transition_timestamp_local).days
    days = days if stopped_reason != '' else 0
    stopped_times_str = "InstanceID: " + instance['InstanceId'] + "," + ' Instance Name: ' +name + "," + " Shutdown Time: " + str(transition_timestamp_format) + "," + " Last Login: " + event +  " Number of days stopped: " + str(days)
    stopped_times = [name, str(days)] # test with random values
    msg_stopped.append(stopped_times)
    msg_stopped_str.append(stopped_times_str)
    msg_stopped_str.append("\n")
    stopped_stdout = ''.join(msg_stopped_str)
    return msg_stopped, stopped_stdout

def running_admins(name, instance):       
    event = last_accessed(instance['InstanceId']).strftime(datetime_format)
    instance_ids.append(instance['InstanceId'])
    instance_names.append(name)
    launchtime = instance['LaunchTime']
    launchtime_local = launchtime.astimezone() if launchtime != '' else '1111-11-11 11:11:11+00:00'
    launchtime_format = launchtime_local.strftime(datetime_format)
    days = abs(today_date_local - launchtime_local).days
    days = days if launchtime != '' else 0
    running_times_str = "InstanceID: " + instance['InstanceId'] + "," + ' Instance Name: ' +name + "," + " Launch Time: " + str(launchtime_format)+ "," + " Last Login: " + event + "," + " Number of days running: " + str(days)
    running_times = [name, str(days)]
    msg_running.append(running_times)
    msg_running_str.append(running_times_str)
    msg_running_str.append("\n")
    running_stdout = ''.join(msg_running_str)
    return msg_running, running_stdout

def last_accessed(instance):
    try:
        event = cloudtrail.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'ResourceName',
                'AttributeValue': instance
            },
             {
                'AttributeKey': 'EventName',
                'AttributeValue': 'AssumeRole'
            },
            {
                'AttributeKey': 'EventSource',
                'AttributeValue': "sts.amazonaws.com"
            }
        ],
        MaxResults=50,
        )
        access_time =  event['Events'][0]['EventTime']
        return access_time
    except Exception as e:
        print(f'Error finding last accessed time: {e}')

###################################################################################
# def last_accessed2():
#     event = cloudtrail.lookup_events(
#         LookupAttributes=[
#             {
#                 'AttributeKey': 'ResourceName',
#                 'AttributeValue': "i-06ca1a363c85ddd2f"
#             },
#              {
#                 'AttributeKey': 'EventName',
#                 'AttributeValue': 'AssumeRole'
#             },
#             {
#                 'AttributeKey': 'EventSource',
#                 'AttributeValue': "sts.amazonaws.com"
#             }
#         ],
#     MaxResults=50,
#     # EventCategory='insight'
#     )
#     # return event['Events'][0]['EventTime']
#     access_time = event['Events'][0]['EventTime']
#     # access_time2 = json.loads(access_time)
#     print(type(access_time))
#     print(access_time.strftime(datetime_format)) 
    
##########################################################################################################

def write_running_csv(data):
    header_running = ['Instance Name', 'Number of days running']
    with open(running_file, 'w') as admins_running:
        writer = csv.writer(admins_running)
        writer.writerow(header_running)
        writer.writerows(data)

def write_stopped_csv(data):
    header_stopped = ['Instance Name', 'Number of days stopped']
    with open(stopped_file, 'w') as admins_stopped:
        writer = csv.writer(admins_stopped)
        writer.writerow(header_stopped)
        writer.writerows(data)

def bar_graph_running(file):
    plt.figure(1)
    data = pandas.read_csv(file)
    df = pandas.DataFrame(data)
    X = list(df.iloc[:, 0])
    Y = list(df.iloc[:, 1])
    plt.bar(X, Y, color='g')
    plt.title("Running Admins")
    plt.ylabel("Number of days running")
    plt.xlabel("Instance Name")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    #plt.show()
    return plt.figure(1)

def bar_graph_stopped(file):
    plt.figure(2)
    data = pandas.read_csv(file)
    df = pandas.DataFrame(data)
    X = list(df.iloc[:, 0])
    Y = list(df.iloc[:, 1])
    plt.bar(X, Y, color='r')
    plt.title("Stopped Admins")
    plt.ylabel("Number of days stopped")
    plt.xlabel("Instance Name")
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.15)
    plt.bar(X, Y, color='r')
    plt.tight_layout()
    # plt.show()
    return plt.figure(2)

def pie_chart():
    pass

main()