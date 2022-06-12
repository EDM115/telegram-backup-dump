# (c) EDM115 - 2022
# No rights reserved, this is open source sir 😘

# async
import os
import logging
import time
from pyrogram import Client, errors, filters, idle
from pyrogram.types import Message, ChatMember
from pyrogram.errors import FloodWait, RPCError, ValueError
from Config import *

# Initialize the client here
teledump = Client(
        "TeleDump",
        api_id = Config.API_ID,
        api_hash = Config.API_HASH,
        bot_token = Config.BOT_TOKEN,
        sleep_threshold = 10
    )

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.FileHandler('log.txt'), logging.StreamHandler()],
    format="%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s"
)
LOGGER = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARN)

# Needed vars there
global idtodump, startrange, stoprange, dumpid, tagged, currentpost, howmanyposts, postlist
idtodump = None
startrange = 1
stoprange = None
dumpid = int()
tagged = True
currentpost = int()
howmanyposts = int()
postlist = []

# Logic here, will look every 10s at the pyrogram doc

# handle /start with a cute message
@teledump.on_message(filters.command("start"))
async def start_bot(_, message: Message):
    await message.reply_text(text="**Hello {} 👋**\n\nI'm TeleDump, a bot made for saving a whole channel/chat into another one.\nDo **/help** if you're lost 😉".format(message.from_user.mention), disable_web_page_preview=True)

@teledump.on_message(filters.command("help"))
async def help_me(_, message: Message):
    await message.reply_text(text="https://telegra.ph/TeleDump-help-12-06")

# handle /backup with a verification (if id/name exists). If not : error message. If private : request to add bot. If ok : adds to idtodump
@teledump.on_message(filters.command("backup"))
async def backup(_, message: Message):
    repliedmess = await message.reply("`Processing… ⏳`")
    try:
        idtodump = message.text.split(None, 1)[1]
    except:
        return await repliedmess.edit("Provide a chat\nCan be in format of `@something` or `-100×××××××××`")
    try:
        await teledump.get_chat(chat_id=idtodump)
    except ValueError:
        return await repliedmess.edit("The chat given is incorrect. Either it doesn't exist, or it's private and you must add me to it with admin rights\n\nCorrect format is : `something` if it's @something, or `-100×××××××` if it's t.me/joinchat/100×××××××")
    await repliedmess.edit(f"{idtodump} successfully added 👌\nNow, use **/range** if needed, **/dump** otherwise")

# handle /range if it's sent. Modify the startrange and stoprange with correct positive values. Checks latest post id on idtodump
@teledump.on_message(filters.command("range"))
async def range(_, message: Message):
    rangemess = await message.reply("`Processing… ⏳`")
    try:
        unsplitted_range = message.text.split(None, 1)[1]
    except:
        return await rangemess.edit("Provide correct values\nFormat : `start_message_id:stop_message_id`\n\nExamples :\n`/range 10:30` : start at the message №10 and ends at the message №30\n`/range 1:456` Start at the beginning of the chat to the message №456\n`/range 666:None` The range starts at the message №666 to the most recent message of the chat of the chat")
    try:
        splitted_range = unsplitted_range.split(":")
        startrange = splitted_range[0]
        stoprange = splitted_range[1]
        # Check if positive
        if startrange > 0 and stoprange > 0:
            pass
        else:
            startrange = 1
            stoprange = None
            raise ValueError("Negative values here")
    except:
        return await rangemess.edit("An unknown error happened while processing your values.\nNote : negative values can't work")
    total_mess = get_chat_history_count(idtodump)
    if startrange > total_mess:
        startrange = 1
        return await rangemess.edit(f"Start (`{startrange}`) is above the chat limit. Choose a lower value")
    if stoprange > total_mess:
        stoprange = None
        return await rangemess.edit(f"Stop (`{stoprange}`) is above the chat limit. Choose a lower value")
    await rangemess.edit(f"Range successfully changed 👌\n\nStarts at {startrange} and stops at {stoprange}")

# handle /dump with same verifs as /backup
@teledump.on_message(filters.command("dump"))
async def dump(_, message: Message):
    dumpmess = await message.reply("`Processing… ⏳`")
    try:
        dumpid = message.text.split(None, 1)[1]
    except:
        return await dumpmess.edit("Provide a chat\nCan be in format of `@something` or `-100×××××××××`\I need to be present there **as administrator**")
    try:
        itsadump = await teledump.get_chat(chat_id=dumpid)
    except ValueError:
        return await dumpmess.edit("The chat given is incorrect. Either it doesn't exist, or it's private and you must add me to it with admin rights\n\nCorrect format is : `something` if it's @something, or `-100×××××××` if it's t.me/joinchat/100×××××××")
    # https://docs.pyrogram.org/api/types/ChatMember#pyrogram.types.ChatMember ADMINISTRATOR check
    imthere = itsadump.get_member(user_id=teledump.id)
    adminornot = imthere.ChatMemberStatus
    if adminornot == "MEMBER":
        await message.reply("I'm a simple member there. Promote me to admin !")
    elif adminornot == "ADMINISTRATOR" or adminornot == "OWNER":
        await message.reply("Enough rights. Good 😌")
    else:
        return dumpmess.edit("There is a problem with the dump. Add me in and make me admin")
    await dumpmess.edit(f"{dumpid} successfully added 👌\nNow, use **/range** if needed, **/dump** otherwise")


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


# Run the bot
#teledump.start()
#idle()
teledump.run()
