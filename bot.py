import discord
from datetime import datetime
from discord import Option
from discord.ext import commands
from discord.ext.commands import MissingPermissions

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
    embed = discord.Embed(title="Banned Users", description="List of banned users", color=0x00ff00, timestamp=datetime.utcnow())
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
        await ctx.send("You don't have the required permissions to run this command.")
    else:
        await ctx.respond(f"Something went wrong, I couldn't unban this member or the member isn't banned. Error: {error}")
        raise error

#ban command

@bot.slash_command(guild_ids=servers, name="ban", description="Ban a user")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, reason: str = None):
    if member.id == ctx.author.id:
        await ctx.send("You can't ban yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator:
        await ctx.send("You can't ban an admin!")
        return
    else:
        if reason is None:
            reason = f"No reason provided."
        await member.send(f"You have been banned from {ctx.guild.name} for {reason}")
        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"{member.mention} has been banned by {ctx.author.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been banned by {ctx.author.mention} for {reason}")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have the required permissions to run this command.")
    else:
        await ctx.send(f"Something went wrong, I couldn't ban this member. Error: {error}")
        raise error


    
#kick command

@bot.slash_command(guild_ids=servers, name="kick", description="Kick a user")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, reason: str = None):
    if member.id == ctx.author.id:
        await ctx.send("You can't kick yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator:
        await ctx.send("You can't kick an admin!")
        return
    else:
        if reason is None:
            reason = f"No reason provided."
        await member.send(f"You have been kicked from {ctx.guild.name} for {reason}")
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f"{member.mention} has been kicked by {ctx.author.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been kicked by {ctx.author.mention} for {reason}")
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions):
        await ctx.send("You don't have the required permissions to run this command.")
    else:
        await ctx.send(f"Something went wrong, I couldn't ban this member. Error: {error}")
        raise error







@bot.event
async def on_ready():
    print("Ready!")

bot.run("MTEzNjQ1ODYwOTAyNzQ2NTI4Ng.Gb0zt7.zl51zpPt9f4T-H_QrZBaz3c2W4PxPEls55IP0k")