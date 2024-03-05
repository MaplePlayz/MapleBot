import discord
from discord import app_commands

intens = discord.Intents.default()
client = discord.Client(intents=intens)
tree = app_commands.CommandTree(client)

guild_id = 1173725609382400101  # Hier kun je de gewenste guild-ID plaatsen

@tree.command(
    name="hello",
    description="My first application Command",
    guild=discord.Object(id=guild_id)
)
async def first_command(interaction):
    await interaction.response.send_message("Hello!")

#admin commando's
@tree.command(
    name="kick",
    description="Kick a user",
    guild=discord.Object(id=guild_id)
)
async def kick(interaction, user: discord.Member, reason: str):
    required_roles = [1173725609382400106, 1173729989670223882]
    member_roles = [role.id for role in interaction.user.roles]

    if any(role_id in member_roles for role_id in required_roles):
        await user.send(f"Je bent gekickt van {interaction.guild.name} voor {reason}")
        await user.kick(reason=reason)
        await interaction.response.send_message(f"{user} is gekickt voor {reason}")
    else:
        await interaction.response.send_message("Je hebt hier geen premissies voor.")












@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1173725609382400101))
    print("Ready!")



client.run("MTEzNjQ1ODYwOTAyNzQ2NTI4Ng.Gb0zt7.zl51zpPt9f4T-H_QrZBaz3c2W4PxPEls55IP0k")