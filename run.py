import client
from discord import Intents

intents = Intents.all()

client = client.PlayBot(intents=intents)
client.run('TOKEN')