# (c) EDM115 - 2022
# No rights reserved, this is open source sir 😘

# async
from pyrogram import Client
from Config import *

# Initialize the client here


# Needed vars there

btoken = Config.BOT_TOKEN
idtodump = None
startrange = 1
stoprange = None
dumpid = int()
tagged = True
currentpost = int()
postlist = int()

# Logic here, will look every 10s at the pyrogram doc

# handle /start with a cute message

# handle /backup with a verification (if id/name exists). If not : error message. If private : request to add bot. If ok : adds to idtodump

# handle /range if it's sent. Modify the startrange and stoprange with correct positive values. Checks latest post id on idtodump

# handle /dump with same verifs as /backup

# handle /tag and modify tagged with True or False

# def /go
"""
The logic is defined here :

Verify if previous commands have been sent and are ok
Send a message to the command sender + in ✨logs✨ (not mandatory so add an iflogs() in Config)
Does for currentpost in postlist (overflowed by start and stop ranges):
    if tagged (else use another thing without forward tag):
        try forward currentpost to dumpid
        except -> idremember: time.sleep || error: wait&retry or counterrors+=1 && listerrors.append(currentpost)
        edit the message each 10 messages forwarded with success and error counts
    in the end, send a message with list of failed messages + their links. So end user can try to check if they exists or no (but mostly it will be deleted posts so yea…)
"""
