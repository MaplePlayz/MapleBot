import discord
from discord import app_commands

intens = discord.Intents.default()
client = discord.Client(intents=intens)
tree = app_commands.CommandTree(client)

@tree.command(
    name="commandname",
    description="My first application Command",
    guild=discord.Object(id=1173978170723151973)
)
async def first_command(interaction):
    await interaction.response.send_message("Hello!")

@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1173978170723151973))
    print("Ready!")

client.run("token")