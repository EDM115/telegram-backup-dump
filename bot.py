# (c) EDM115 - 2022
# No rights reserved, this is open source sir 😘

# async
import os
import logging
import time
from types import BooleanType as blTyp
from pyrogram import Client, errors, filters, idle
from pyrogram.types import Message, ChatMember
from pyrogram.errors import FloodWait, RPCError
from config import *

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
    handlers=[logging.FileHandler('logs.txt'), logging.StreamHandler()],
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
    await message.reply_text(text="**https://telegra.ph/TeleDump-help-12-06**")

# handle /backup with a verification (if id/name exists). If not : error message. If private : request to add bot. If ok : adds to idtodump
@teledump.on_message(filters.command("backup"))
async def backup(_, message: Message, idtodump):
    repliedmess = await message.reply("`Processing… ⏳`")
    try:
        idtodump = message.text.split(None, 1)[1]
    except:
        return await repliedmess.edit("Provide a chat\nCan be in format of `@something` or `-100×××××××××`")
    try:
        await teledump.get_chat(chat_id=idtodump)
    except ValueError:
        LOGGER.warn(f"Incorrect chat in /backup : {idtodump}")
        return await repliedmess.edit("The chat given is incorrect. Either it doesn't exist, or it's private and you must add me to it with admin rights\n\nCorrect format is : `something` if it's @something, or `-100×××××××` if it's t.me/joinchat/100×××××××")
    await repliedmess.edit(f"{idtodump} successfully added 👌\nNow, use **/range** if needed, **/dump** otherwise")

# handle /range if it's sent. Modify the startrange and stoprange with correct positive values. Checks latest post id on idtodump
@teledump.on_message(filters.command("range"))
async def range(_, message: Message, startrange, stoprange):
    rangemess = await message.reply("`Processing… ⏳`")
    try:
        unsplitted_range = message.text.split(None, 1)[1]
    except:
        return await rangemess.edit("Provide correct values\nFormat : `start_message_id:stop_message_id`\n\nExamples :\n`/range 10:30` : start at the message №10 and ends at the message №30\n`/range 1:456` Start at the beginning of the chat to the message №456\n`/range 666:None` The range starts at the message №666 to the most recent message of the chat of the chat")
    try:
        splitted_range = unsplitted_range.split(":")
        startrange = int(splitted_range[0])
        stoprange = int(splitted_range[1])
        # Check if positive
        if startrange > 0 and stoprange > 0:
            pass
        else:
            startrange = 1
            stoprange = None
            raise ValueError("Negative values here")
    except:
        return await rangemess.edit("An unknown error happened while processing your values.\nNote : negative values can't work")
    total_mess = teledump.get_chat_history_count(idtodump)
    if startrange > total_mess:
        startrange = 1
        return await rangemess.edit(f"Start (`{startrange}`) is above the chat limit. Choose a lower value")
    if stoprange > total_mess:
        stoprange = None
        return await rangemess.edit(f"Stop (`{stoprange}`) is above the chat limit. Choose a lower value")
    await rangemess.edit(f"Range successfully changed 👌\n\nStarts at `{startrange}` and stops at `{stoprange}`")

# handle /dump with same verifs as /backup
@teledump.on_message(filters.command("dump"))
async def dump(_, message: Message, dumpid):
    dumpmess = await message.reply("`Processing… ⏳`")
    try:
        dumpid = message.text.split(None, 1)[1]
    except:
        return await dumpmess.edit("Provide a chat\nCan be in format of `@something` or `-100×××××××××`\nI need to be present there **as administrator**")
    try:
        itsadump = await teledump.get_chat(chat_id=dumpid)
    except KeyError:
        LOGGER.warn(f"KeyError in /dump with {dumpid}")
        return await dumpmess.edit("This chat doesn't exist\n\nCorrect format is : `something` if it's @something, or `-100×××××××` if it's t.me/joinchat/100××××××× or t.me/c/××××××")
    except PeerIdInvalid:
        LOGGER.warn(f"PeerIdInvalid in /dump with {dumpid}")
        return await dumpmess.edit("You need to add me there ! And give me admin rights ☺️")
    except:
        LOGGER.warn(f"Unknown error in /dump with {dumpid}")
        return await dumpmess.edit("The chat given is incorrect. Either it doesn't exist, or it's private and you must add me to it with admin rights\n\nCorrect format is : `something` if it's @something, or `-100×××××××` if it's t.me/joinchat/100×××××××")
    """
    Headache here 💀 Idk how to get the ID of the bot itself + useless verification
    # https://docs.pyrogram.org/api/types/ChatMember#pyrogram.types.ChatMember ADMINISTRATOR check
    imthere = itsadump.get_member(user_id=teledump.id)
    adminornot = imthere.ChatMemberStatus
    if adminornot == "MEMBER":
        await message.reply("I'm a simple member there. Promote me to admin !")
    elif adminornot == "ADMINISTRATOR" or adminornot == "OWNER":
        await message.reply("Enough rights. Good 😌")
    else:
        return dumpmess.edit("There is a problem with the dump. Add me in and make me admin")
    """
    await dumpmess.edit(f"{dumpid} successfully added 👌\nTime for **/tag** if needed, otherwise **/go**")

# handle /tag and modify tagged with True or False
@teledump.on_message(filters.command("tag"))
async def tag(_, message: Message, tagged):
    tagmess = await message.reply("`Processing… ⏳`")
    try:
        tagged = message.text.split(None, 1)[1]
    except:
        return await tagmess.edit("Provide a value. Must be `True` or `False` (case sensitive)")
    if not isinstance(tagged, blTyp):
        return await tagmess.edit("Provide a correct value. Must be `True` or `False` (case sensitive)")
    if tagged:
        await tagmess.edit("Successfully changed 👌 Messages will be send with forward tag")
    else:
        await tagmess.edit("Successfully changed 👌 Messages will be send without forward tag")

# def /go
"""
The logic is defined here :

Verify if previous commands have been sent and are ok
Send a message to the command sender + in ✨logs✨ (not mandatory so add an iflogs() in Config)
Does for currentpost in postlist (overflowed by start and stop ranges):
    if tagged (else use another thing without forward tag -> send_message() creates a copy):
        try forward currentpost to dumpid
        except -> toomuchcattempts: time.sleep || error: wait&retry or counterrors+=1 && listerrors.append(currentpost)
        edit the message each 10 messages forwarded with success and error counts
    in the end, send a message with list of failed messages + their links. So end user can try to check if they exists or no (but mostly it will be deleted posts/system messages so yea…)
"""

# Added /log for bug tracking
@teledump.on_message(filters.command("log"))
async def send_logs(_, message: Message):
    with open('logs.txt', 'rb') as doc_f:
        try:
            await teledump.send_document(
                chat_id=message.chat.id,
                document=doc_f,
                file_name=doc_f.name,
                reply_to_message_id=message.id
            )
            LOGGER.info(f"Log file sent to {message.from_user.id}")
        except FloodWait as e:
            sleep(e.x)
        except RPCError as e:
            message.reply_text(e, quote=True)
            LOGGER.warn(f"Error in /log : {e}")

# /var for sending the variables. Useful to know what have been modified
# async def send_vars(_, message: Message, idtodump, startrange, stoprange, dumpid, tagged, currentpost, howmanyposts, postlist):
@teledump.on_message(filters.command("var"))
async def send_vars(_, message: Message):
    all_vars = f"""
**All variables at {time.strftime("%Y/%m/%d - %H:%M:%S")} :**

idtodump = `{idtodump}`
startrange = `{startrange}`
stoprange = `{stoprange}`
dumpid = `{dumpid}`
tagged = `{tagged}`
currentpost = `{currentpost}`
howmanyposts = `{howmanyposts}`
postlist = `{postlist}`
    """
    await message.reply(text=all_vars)

# Run the bot
LOGGER.info("We start captain !")
teledump.run()
