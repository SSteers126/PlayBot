import commands
from discord import Intents

intents = Intents.all()

client = commands.PlayBot(intents=intents)
client.run('TOKEN')