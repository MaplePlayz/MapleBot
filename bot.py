import discord
from discord import app_commands

intens = discord.Intents.default()
client = discord.Client(intents=intens)
tree = app_commands.CommandTree(client)

guild_id = 1173725609382400101  # Hier kun je de gewenste guild-ID plaatsen
admin_roles = [1173725609382400106, 1173729989670223882]  # Hier kun je de gewenste admin-role ID's plaatsen
muted_role = 1197094790379089971  # Hier kun je de gewenste muted-role ID plaatsen

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
#kick commando
async def kick(interaction, user: discord.Member, reason: str):
    required_roles = admin_roles
    member_roles = [role.id for role in interaction.user.roles]

    if any(role_id in member_roles for role_id in required_roles):
        await user.send(f"Je bent gekickt van {interaction.guild.name} voor {reason}")
        await user.kick(reason=reason)
        await interaction.response.send_message(f"{user} is gekickt voor {reason}")
    else:
        await interaction.response.send_message("Je hebt hier geen premissies voor.")
#ban commando
@tree.command(
    name="ban",
    description="Ban a user",
    guild=discord.Object(id=guild_id)
)
async def ban(interaction, user: discord.Member, reason: str):
    required_roles = admin_roles
    member_roles = [role.id for role in interaction.user.roles]

    if any(role_id in member_roles for role_id in required_roles):
        await user.send(f"Je bent geband van {interaction.guild.name} voor {reason}")
        await user.ban(reason=reason)
        await interaction.response.send_message(f"{user} is geband voor {reason}")
    else:
        await interaction.response.send_message("Je hebt hier geen premissies voor.")

#unban commando
# @tree.command(
#     name="unban",
#     description="Unban a user",
#     guild=discord.Object(id=guild_id)
# )
# async def unban(interaction, user_id: int):
#             required_roles = admin_roles
#             member_roles = [role.id for role in interaction.user.roles]

#             if any(role_id in member_roles for role_id in required_roles):
#                 banned_users = await interaction.guild.bans()
#                 for ban_entry in banned_users:
#                     if ban_entry.user.id == int(user_id):  # Convert user_id to an integer
#                         await interaction.guild.unban(ban_entry.user)
#                         await interaction.response.send_message(f"Gebruiker met ID {user_id} kan de server weer in.")
#                         return
#                 await interaction.response.send_message(f"Gebruiker met ID {user_id} is niet verbannen.")
#             else:
#                 await interaction.response.send_message("Je hebt hier geen premissies voor.")

#mute commando
@tree.command(
    name="mute",
    description="Mute a user",
    guild=discord.Object(id=guild_id)
)
async def mute(interaction, user: discord.Member, reason: str):
    required_roles = admin_roles
    member_roles = [role.id for role in interaction.user.roles]
    if any(role_id in member_roles for role_id in required_roles):
        await user.add_roles(discord.Object(id=muted_role))
        await user.send(f"Je bent gemute van {interaction.guild.name} voor {reason}")
        await interaction.response.send_message(f"{user} is gemute voor {reason}")
    else:
        await interaction.response.send_message("Je hebt hier geen premissies voor.")
                
#unmute commando
@tree.command(
    name="unmute",
    description="Unmute a user",
    guild=discord.Object(id=guild_id)
)
async def unmute(interaction, user: discord.Member,):
    required_roles = admin_roles
    member_roles = [role.id for role in interaction.user.roles]
    if any(role_id in member_roles for role_id in required_roles):
        await user.remove_roles(discord.Object(id=muted_role))
        await user.send(f"Je bent geunmute van {interaction.guild.name}")
        await interaction.response.send_message(f"{user} is geunmute")
    else:
        await interaction.response.send_message("Je hebt hier geen premissies voor.")









@client.event
async def on_ready():
    await tree.sync(guild=discord.Object(id=1173725609382400101))
    print("Ready!")



client.run("MTEzNjQ1ODYwOTAyNzQ2NTI4Ng.Gb0zt7.zl51zpPt9f4T-H_QrZBaz3c2W4PxPEls55IP0k")