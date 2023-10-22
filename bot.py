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

token="1486232044:AAH1DTSvr9ySFKkfIH3LjNpQ2mFwA8ERL5U"
instance='i-0c65c4c3127999e85'
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

bot = telegram.Bot(token=token)
print(bot.get_me())
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

SERVER_STOPPED = 0
SERVER_STARTING = 1
SERVER_STARTED = 2
SERVER_RUNNING = 3

statuses = {
    "stopped": SERVER_STOPPED,
    "starting": SERVER_STARTING,
    "started": SERVER_STARTED,
    "running": SERVER_RUNNING
}

def __get_status__():
    statuses = subprocess.check_output("aws ec2 describe-instance-status --include-all-instances", shell=True)
    statuses = json.loads(statuses)
    for status in statuses['InstanceStatuses']:
        if status['InstanceId'] == instance:
            curStatus = status['InstanceState'][' Name']
            return statuses.get(curStatus, curStatus)
    return None

def __start_server__():
    os.system("aws ec2 start-instances --instance-ids " + instance)

def __stop_server__():
    os.system("aws ec2 stop-instances --instance-ids " + instance)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! Welcome to Valo Bot, I am a very useful bot that helps you get one step closer to wasting your life.")


def check_server_status(update, context, action, fstart=False):
    msg = context.bot.send_message(chat_id=update.effective_chat.id, text=f"Checking Server Status for {action}...")
    status = __get_status__()
    if status == SERVER_STARTED and action == "start":
        if not fstart:
            msg.edit_text("Server is already started")
    elif status == SERVER_STOPPED and action == "stop":
        if not fstart:
            msg.edit_text("Server is already stopped")
    elif status == SERVER_STARTED and action == "stop":
        __stop_server__()
        if not fstart:
            msg.edit_text("Server is stopping")
        while __get_status__() != SERVER_STOPPED:
            time.sleep(2)
        if not fstart:
            msg.edit_text("Server Stopped")
    elif status == SERVER_STOPPED and action == "start":
        __start_server__()
        if not fstart:
            msg.edit_text("Server is starting")
        while __get_status__() != SERVER_STARTED:
            time.sleep(2)
        if not fstart:
            msg.edit_text("Server Started")
    elif status is None:
        if not fstart:
            msg.edit_text("Server not found")
    else:
        if not fstart:
            msg.edit_text(f"Server is in {status} state")

def starts(update, context):
    check_server_status(update, context, "start")

def stops(update, context):
    check_server_status(update, context, "stop")

def restart(update, context):
    check_server_status(update, context, "stop")
    check_server_status(update, context, "start")

# sometimes a single start doesn't work, so we try twice start, stop, start
def fstart(update, context):
    check_server_status(update, context, "start")
    check_server_status(update, context, "stop")
    check_server_status(update, context, "start")

functions=[start, starts, stops, restart, fstart]

def help(update, context):
    # Send all available commands
    helptxt = "Available commands:\n"
    helptxt += "/starts - Start the server\n"
    helptxt += "/stops - Stop the server, it can take upto 3-4 minutes\n"
    helptxt += "/help - Show this help message\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=helptxt)

functions.append(help)

for function in functions:
    handler = CommandHandler(function.__name__, function)
    dispatcher.add_handler(handler)

def main():
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
