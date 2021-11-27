import commands
from discord import Intents

# import dl.yt
intents = Intents.all()

client = commands.PlayBot(intents=intents)
client.run('token')

# $play https://www.youtube.com/watch?v=dbevJM-2lcY