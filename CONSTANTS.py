from os.path import dirname, abspath
from asyncio import Queue

ROOT_DIR = dirname(abspath(__file__))
MEDIA_DIR = ROOT_DIR + r"\media"
FF_DIR = ROOT_DIR + r"\ffmpeg\ffmpeg.exe"
VOICE = None
SONGQUEUE = Queue()

# Keeping .lower() so in case the prefix is changed, consistency is kept
PREFIX = "$".lower()
# Length of usernames after # (inclusive), i.e Name[#1234]
TAGLEN = 5

# BlackJack data
HIT = "👊"
FOLD = "✋"
REPLAY = "🟢"
NOREPLAY = "🔴"