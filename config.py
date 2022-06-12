import os

class Config(object):
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    LOGS_CHANNEL = int(os.environ.get("LOGS_CHANNEL", None))
