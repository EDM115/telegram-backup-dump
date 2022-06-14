# (c) EDM115 - 2022
# No rights reserved, this is open source sir 😘

# async
import os
import logging
import time
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

# handle /start with a cute message
@teledump.on_message(filters.command("start"))
async def start_bot(_, message: Message):
    await message.reply_text(text="**Hello {} 👋**\n\nI'm TeleDump, a bot made for saving a whole channel/chat into another one.\nDo **/help** if you're lost 😉".format(message.from_user.mention), disable_web_page_preview=True)

@teledump.on_message(filters.command("help"))
async def help_me(_, message: Message):
    await message.reply_text(text="**https://telegra.ph/TeleDump-help-12-06**")

# Mandatory /begin to avoid problems
@teledump.on_message(filters.command("begin"))
async def begin(_, message: Message):
    try:
        Var.currentuser = message.from_user.id
    except:
        return await message.reply_text("Unknown error")
    await message.reply_text("Good 😌 you can now use me\nStart with **/backup**")

# handle /backup with a verification (if id/name exists). If not : error message. If private : request to add bot. If ok : adds to idtodump
@teledump.on_message(filters.command("backup"))
async def backup(_, message: Message):
    if Var.currentuser != 0:
        repliedmess = await message.reply("`Processing… ⏳`")
        try:
            Var.idtodump = message.text.split(None, 1)[1]
        except:
            return await repliedmess.edit("Provide a chat\nCan be in format of `@something` or `-100×××××××××`")
        try:
            await teledump.get_chat(chat_id=Var.idtodump)
        except ValueError:
            LOGGER.warn(f"Incorrect chat in /backup : {idtodump}")
            return await repliedmess.edit("The chat given is incorrect. Either it doesn't exist, or it's private and you must add me to it with admin rights\n\nCorrect format is : `something` if it's @something, or `-100×××××××` if it's t.me/joinchat/100×××××××")
        await repliedmess.edit(f"{Var.idtodump} successfully added 👌\nNow, use **/range** if needed, **/dump** otherwise")
    elif Var.currentuser != message.from_user.id:
        return await message.reply_text("Another user is already using me. Theorically I can backup 2 channels at the same time, but better not overuse me 🙂\nTry again later")
    else:
        return await message.reply_text("You need to send **/begin** to authenticate yourself")

# handle /range if it's sent. Modify the startrange and stoprange with correct positive values. Checks latest post id on idtodump
@teledump.on_message(filters.command("range"))
async def range(_, message: Message):
    if Var.currentuser != 0:
        rangemess = await message.reply("`Processing… ⏳`")
        try:
            unsplitted_range = message.text.split(None, 1)[1]
        except:
            return await rangemess.edit("Provide correct values\nFormat : `start_message_id:stop_message_id`\n\nExamples :\n`/range 10:30` : start at the message №10 and ends at the message №30\n`/range 1:456` Start at the beginning of the chat to the message №456\n`/range 666:None` The range starts at the message №666 to the most recent message of the chat of the chat")
        try:
            splitted_range = unsplitted_range.split(":")
            Var.startrange = int(splitted_range[0])
            Var.stoprange = int(splitted_range[1])
            # Check if positive
            if Var.startrange > 0 and Var.stoprange > 0:
                pass
            else:
                Var.startrange = 1
                Var.stoprange = None
                raise ValueError("Negative values here")
        except:
            return await rangemess.edit("An unknown error happened while processing your values.\nNote : negative values can't work")
        total_mess = teledump.get_chat_history_count(Var.idtodump)
        if Var.startrange > total_mess:
            Var.startrange = 1
            return await rangemess.edit(f"Start (`{Var.startrange}`) is above the chat limit. Choose a lower value")
        if Var.stoprange > total_mess:
            Var.stoprange = None
            return await rangemess.edit(f"Stop (`{Var.stoprange}`) is above the chat limit. Choose a lower value")
        await rangemess.edit(f"Range successfully changed 👌\n\nStarts at `{Var.startrange}` and stops at `{Var.stoprange}`")
    elif Var.currentuser != message.from_user.id:
        return await message.reply_text("Another user is already using me. Theorically I can backup 2 channels at the same time, but better not overuse me 🙂\nTry again later")
    else:
        return await message.reply_text("You need to send **/begin** to authenticate yourself")

# handle /dump with same verifs as /backup
@teledump.on_message(filters.command("dump"))
async def dump(_, message: Message):
    if Var.currentuser != 0:
        dumpmess = await message.reply("`Processing… ⏳`")
        try:
            Var.dumpid = message.text.split(None, 1)[1]
        except:
            return await dumpmess.edit("Provide a chat\nCan be in format of `@something` or `-100×××××××××`\nI need to be present there **as administrator**")
        try:
            itsadump = await teledump.get_chat(chat_id=Var.dumpid)
        except KeyError:
            LOGGER.warn(f"KeyError in /dump with {Var.dumpid}")
            return await dumpmess.edit("This chat doesn't exist\n\nCorrect format is : `something` if it's @something, or `-100×××××××` if it's t.me/joinchat/100××××××× or t.me/c/××××××")
        except PeerIdInvalid:
            LOGGER.warn(f"PeerIdInvalid in /dump with {Var.dumpid}")
            return await dumpmess.edit("You need to add me there ! And give me admin rights ☺️")
        except:
            LOGGER.warn(f"Unknown error in /dump with {Var.dumpid}")
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
        await dumpmess.edit(f"{Var.dumpid} successfully added 👌\nTime for **/tag** if needed, otherwise **/go**")
    elif Var.currentuser != message.from_user.id:
        return await message.reply_text("Another user is already using me. Theorically I can backup 2 channels at the same time, but better not overuse me 🙂\nTry again later")
    else:
        return await message.reply_text("You need to send **/begin** to authenticate yourself")

# handle /tag and modify tagged with True or False
@teledump.on_message(filters.command("tag"))
async def tag(_, message: Message):
    if Var.currentuser != 0:
        tagmess = await message.reply("`Processing… ⏳`")
        try:
            Var.tagged = message.text.split(None, 1)[1]
        except:
            return await tagmess.edit("Provide a value. Must be `True` or `False` (case sensitive)")
        if not isinstance(tagged, bool):
            return await tagmess.edit("Provide a correct value. Must be `True` or `False` (case sensitive)")
        if Var.tagged:
            await tagmess.edit("Successfully changed 👌 Messages will be send with forward tag")
        else:
            await tagmess.edit("Successfully changed 👌 Messages will be send without forward tag")
    elif Var.currentuser != message.from_user.id:
        return await message.reply_text("Another user is already using me. Theorically I can backup 2 channels at the same time, but better not overuse me 🙂\nTry again later")
    else:
        return await message.reply_text("You need to send **/begin** to authenticate yourself")

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
    resets all values from Var to their original
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
@teledump.on_message(filters.command("var"))
async def send_vars(_, message: Message):
    all_vars = f"""
**All variables at {time.strftime("%Y/%m/%d - %H:%M:%S")} :**

currentuser = `{Var.currentuser}`
idtodump = `{Var.idtodump}`
startrange = `{Var.startrange}`
stoprange = `{Var.stoprange}`
dumpid = `{Var.dumpid}`
tagged = `{Var.tagged}`
currentpost = `{Var.currentpost}`
howmanyposts = `{Var.howmanyposts}`
postlist = `{Var.postlist}`
    """
    await message.reply(text=all_vars)

# Resets all values to origin
@teledump.on_message(filters.command("cancel"))
async def cancel(_, message: Message):
    cancelmess = await message.replytext("`Processing… ⏳`")
    try:
        Var.currentuser = int()
        Var.idtodump = None
        Var.startrange = 1
        Var.stoprange = None
        Var.dumpid = int()
        Var.tagged = True
        Var.currentpost = int()
        Var.howmanyposts = int()
        Var.postlist = []
    except:
        return await cancelmess.edit("An error happened 😕")
    await cancelmess.edit("Successfully cancelled all 😌")

# Run the bot
LOGGER.info("We start captain !")
teledump.run()
