import discord
from discord import Option
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from datetime import datetime, timedelta

admin_roles = [1173725609382400106, 1173729989670223882]  # Hier kun je de gewenste admin-role ID's plaatsen
muted_role = 1197094790379089971  # Hier kun je de gewenste muted-role ID plaatsen
log_channel_id = 1173725610309341401

bot = discord.Bot()

servers = [1173725609382400101]

#Administrator commands

#banlist command

@bot.slash_command(guild_ids=servers, name="banlist", description="Get list of banned users")
@commands.has_permissions(ban_members=True)
async def banlist(ctx):
    await ctx.defer()
    embed = discord.Embed(title="Banned Users", description="List of banned users", color=0x00ff00, timestamp=datetime.utcnow() + timedelta(hours=1))
    async for entry in ctx.guild.bans():
        if len(embed.fields) >= 25:
            break
        if len(embed) > 5900:
            embed.add_field(name="Banned Users", value="Too many users to display")
        else:
            embed.add_field(name=f"ban", value = f"Username: {entry.user.name}#{entry.user.discriminator}\nID: {entry.user.id}\nReason: {entry.reason}")
            
    await ctx.respond(embed=embed)
    
    
#unban command

@bot.slash_command(guild_ids=servers, name="unban", description="Unban a user")
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: str = discord.Option(name="user", description="The user to unban", required=True)):
    await ctx.defer()
    try:
        user_id = int(user)
    except ValueError:
        await ctx.send("Please provide a valid user ID.")
        return
    
    member = await bot.fetch_user(user_id)
    await ctx.guild.unban(member)
    await ctx.respond(f"Unbanned {member.mention}")
    log_channel = bot.get_channel(log_channel_id)
    await log_channel.send(f"{member.mention} has been unbanned by {ctx.author.mention} ")
@bot.event
async def on_application_command_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You don't have the required permissions to run this command.")
    else:
        await ctx.respond(f"Something went wrong, I couldn't unban this member or the member isn't banned. Error: {error}")
        raise error

#ban command

@bot.slash_command(guild_ids=servers, name="ban", description="Ban a user")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: Option(discord.Member, description="The member to ban"), reason: Option(str, description="why?", required=False)):
    if member.id == ctx.author.id:
        await ctx.respond("You can't ban yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator:
        await ctx.respond("You can't ban an admin!")
        return
    else:
        if reason is None:
            reason = f"No reason provided by {ctx.author.name}"
        await member.send(f"You have been banned from {ctx.guild.name} for {reason}")
        await ctx.guild.ban(member, reason=reason)
        await ctx.respond(f"You have banned {member.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been banned by {ctx.author.mention} for {reason}")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You don't have the required permissions to run this command.")
    else:
        await ctx.respond(f"Something went wrong, I couldn't ban this member. Error: {error}")
        raise error
        
    
#kick command

@bot.slash_command(guild_ids=servers, name="kick", description="Kick a user")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: Option(discord.Member, description="The member to ban"), reason: Option(str, description="why?", required=False)):
    if member.id == ctx.author.id:
        await ctx.respond("You can't kick yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator:
        await ctx.respond("You can't kick an admin!")
        return
    else:
        if reason is None:
            reason = f"No reason provided by {ctx.author.name}"
        await member.send(f"You have been kicked from {ctx.guild.name} for {reason}")
        await ctx.guild.ban(member, reason=reason)
        await ctx.respond(f"You have kicked {member.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been kicked by {ctx.author.mention} for {reason}")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You don't have the required permissions to run this command.")
    else:
        await ctx.respond(f"Something went wrong, I couldn't ban this member. Error: {error}")
        raise error

#mute command
@bot.slash_command(guild_ids=servers, name="mute", description="Mute a user")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: Option(discord.Member, description="The member to mute"), reason: Option(str, description="why?", required=False)):
    if member.id == ctx.author.id:
        await ctx.respond("You can't mute yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator:
        await ctx.respond("You can't mute an admin!")
        return
    if discord.utils.get(member.roles, id=muted_role) is not None:
        await ctx.respond(f"{member.mention} is already muted.")
        return
    else:
        if reason is None:
            reason = f"No reason provided by {ctx.author.name}"
        await member.send(f"You have been muted in {ctx.guild.name} for {reason}")
        await member.add_roles(ctx.guild.get_role(muted_role))
        await ctx.respond(f"you have muted {member.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been muted by {ctx.author.mention} for {reason}")
@mute.error
async def mute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You don't have the required permissions to run this command.")
    else:
        await ctx.respond(f"Something went wrong, I couldn't mute this member. Error: {error}")
        raise error

#unmute command
@bot.slash_command(guild_ids=servers, name="unmute", description="Unmute a user")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: Option(discord.Member, description="The member to unmute")):
    if discord.utils.get(member.roles, id=muted_role) is not None:
        
        await member.remove_roles(ctx.guild.get_role(muted_role))
        await ctx.respond(f"You have unmuted {member.mention}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been unmuted by {ctx.author.mention}")
    else:
        await ctx.respond(f"{member.mention} is not muted.")
@unmute.error
async def unmute_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You don't have the required permissions to run this command.")
    else:
        await ctx.respond(f"Something went wrong, I couldn't unmute this member. Error: {error}")
        raise error

#clear command
@bot.slash_command(guild_ids=servers, name="clear", description="Clear messages")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: Option(int, description="The amount of messages to clear")):
    await ctx.channel.purge(limit=amount)
    await ctx.respond(f"{amount} messages have been cleared")
@clear.error
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.respond("You don't have the required permissions to run this command.")
    else:
        await ctx.respond(f"Something went wrong, I couldn't clear messages. Error: {error}")
        raise error



@bot.event
async def on_ready():
    print("Ready!")

bot.run("")