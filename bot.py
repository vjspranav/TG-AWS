# -*- coding: utf-8 -*-
"""
Created on Wed May 12 01:21:29 2021
@author: vjspranav
"""

import logging
import os
import subprocess
import telegram
import requests
import json
import time
from telegram.ext import Updater
from telegram.ext import CommandHandler, ConversationHandler

token=""
instance=''
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bot = telegram.Bot(token=token)
print(bot.get_me())
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Welcome to Valo Bot")

def starts(update,context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id, text="Checking Server Status...")
    # Check status of instance
    statuses = subprocess.check_output("aws ec2 describe-instance-status --include-all-instances", shell=True)
    statuses = json.loads(statuses)
    # Format:
    #     {
    #     "InstanceStatuses": [
    #         {
    #             "AvailabilityZone": "ap-south-1b",
    #             "InstanceId": "i-0c65c4c3127999e85",
    #             "InstanceState": {
    #                 "Code": 80,
    #                 "Name": "stopped"
    #             },
    #             "InstanceStatus": {
    #                 "Status": "not-applicable"
    #             },
    #             "SystemStatus": {
    #                 "Status": "not-applicable"
    #             }
    #         }
    #     ]
    # }

    # get the entry with instance id
    for status in statuses['InstanceStatuses']:
        if status['InstanceId'] == instance:
            if status['InstanceState']['Name'] == 'started':
                msg.edit_text("Server is already started")
            elif status['InstanceState']['Name'] == 'stopped':
                os.system("aws ec2 start-instances --instance-ids " + instance)
                msg.edit_text("Server is starting")
                break
            else:
                msg.edit_text("Server is in " + status['InstanceState']['Name'] + " state")
            break
    
    # Keep checking status of instance until it is started
    while True:
        statuses = subprocess.check_output("aws ec2 describe-instance-status --include-all-instances", shell=True)
        statuses = json.loads(statuses)
        if statuses['InstanceStatuses'][0]['InstanceState']['Name'] == 'running':
            msg.edit_text("Server Started")
            break
        time.sleep(2)

    # os.system("aws ec2 stop-instances --instance-ids " + instance)
    # msg = context.bot.send_message(chat_id=update.effective_chat.id, text="Checking Server Status [1/4]...")
    # time.sleep(30)
    # os.system("aws ec2 start-instances --instance-ids " + instance)
    # msg.edit_text("Preparing Server [2/4]...")
    # time.sleep(30)
    # os.system("aws ec2 stop-instances --instance-ids " + instance)
    # msg.edit_text("Starting Server [3/4]...")
    # time.sleep(45)
    # os.system("aws ec2 start-instances --instance-ids " + instance)
    # time.sleep(30)
    # msg.edit_text("Server Started [4/4]")

def stops(update,context):
    msg = context.bot.send_message(chat_id=update.effective_chat.id, text="Checking Server Status...")
    statuses = subprocess.check_output("aws ec2 describe-instance-status --include-all-instances", shell=True)
    statuses = json.loads(statuses)
    for status in statuses['InstanceStatuses']:
        if status['InstanceId'] == instance:
            if status['InstanceState']['Name'] == 'stopped':
                msg.edit_text("Server is already stopped")
            elif status['InstanceState']['Name'] == 'running' or status['InstanceState']['Name'] == 'started':
                os.system("aws ec2 stop-instances --instance-ids " + instance)
                msg.edit_text("Server is stopping")
                break
            else:
                msg.edit_text("Server is in " + status['InstanceState']['Name'] + " state")
            break

    while True:
        statuses = subprocess.check_output("aws ec2 describe-instance-status --include-all-instances", shell=True)
        statuses = json.loads(statuses)
        if statuses['InstanceStatuses'][0]['InstanceState']['Name'] == 'stopped':
            msg.edit_text("Server Stopped")
            break
        time.sleep(5)
    # os.system("aws ec2 stop-instances --instance-ids " + instance)
    # context.bot.send_message(chat_id=update.effective_chat.id, text="Server stopped")

functions=[start, starts, stops]

for function in functions:
    handler = CommandHandler(function.__name__, function)
    dispatcher.add_handler(handler)

def main():
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
