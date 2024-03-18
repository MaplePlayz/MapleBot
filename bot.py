import discord
from discord import Option
from discord.ext import commands
from discord.ext.commands import MissingPermissions
from datetime import datetime, timedelta
import yt_dlp
from discord import FFmpegPCMAudio
import os
from collections import deque
import asyncio
import dotenv


admin_roles = [1173725609382400106, 1173729989670223882]  # Hier kun je de gewenste admin-role ID's plaatsen
muted_role = 1197094790379089971  # Hier kun je de gewenste muted-role ID plaatsen
log_channel_id = 1173725610309341401 # Hier kun je de gewenste log-channel ID plaatsen

bot = discord.Bot()

servers = [1173725609382400101] # Hier kun je de gewenste server ID's plaatsen



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
@unban.error
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

#music commands


# Queue to hold songs
song_queue = deque()

@bot.slash_command(guild_ids=servers, name="play", description="Play a song")
async def play(ctx, song: str):
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        await ctx.respond("You are not in a voice channel.")
        return
    #check if the link provided is a playlist trough checking if list= is in the link
    if "list=" in song:
        await ctx.respond("I can't play playlists yet, only single songs.")
        return
    voice_client = ctx.guild.voice_client

    # If there's a voice client but no songs playing, add the song to the queue
    if voice_client and voice_client.is_playing():
        # Add the song to the queue
        song_queue.append(song)
        await ctx.respond(f"{song} has been added to the queue.")
        return

    if voice_client is None:
        voice_client = await voice_channel.connect()

    await ctx.defer()

    await play_song(ctx, song)

async def play_song(ctx, song):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'tempsong',  # filename
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '0',
        }],
        'default_search': 'ytsearch',
        'extractor_args': {
            'youtube': {
                'default_search': 'auto',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '0',
                }],
            },
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(song, download=True)
            #if 'url' in info:
               # url = info['url']
           # elif 'entries' in info:
                # Take the URL of the first video in the playlist
              #  url = info['entries'][0]['url']
           # else:
             #   await ctx.respond("Could not find the URL of the song.")
               # return
        except yt_dlp.DownloadError as e:
            await ctx.respond(f"An error occurred while trying to play the song: {e}")
            return

    try:
        # Play the song
        voice_client = ctx.guild.voice_client
        voice_client.play(discord.FFmpegPCMAudio('tempsong.mp3'), after=lambda e: play_next(ctx))
        await ctx.respond(f"Now playing: {song}")
    except Exception as e:
        await ctx.respond(f"An error occurred while playing the song: {e}")
        # Logging the error
        print(f"Error occurred while playing the song: {e}")

def play_next(ctx):
    voice_client = ctx.guild.voice_client
    if song_queue:
        next_song = song_queue.popleft()
        asyncio.run(play_song(ctx, next_song))
    else:
        # If no more songs in the queue, delete the last song played
        os.remove('tempsong.mp3')

# Skip command
@bot.slash_command(guild_ids=servers, name="skip", description="Skip the current song")
async def skip(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.respond("Song skipped.")
    else:
        await ctx.respond("No song is currently playing.")
@skip.error
async def skip_error(ctx, error):
    await ctx.respond(f"An error occurred while trying to skip the song: {error}")
    raise error

# Stop command
@bot.slash_command(guild_ids=servers, name="stop", description="Stop the music")
async def stop(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        await ctx.respond("Music stopped.")
        voice_client.stop()
        await voice_client.disconnect()
        
    else:
        await ctx.respond("No song is currently playing.")
@stop.error
async def stop_error(ctx, error):
    await ctx.respond(f"An error occurred while trying to stop the music: {error}")
    raise error

# Pause command
@bot.slash_command(guild_ids=servers, name="pause", description="Pause the music")
async def pause(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.pause()
        await ctx.respond("Music paused.")
    else:
        await ctx.respond("No song is currently playing.")
@pause.error
async def pause_error(ctx, error):
    await ctx.respond(f"An error occurred while trying to pause the music: {error}")
    raise error

# Resume command
@bot.slash_command(guild_ids=servers, name="resume", description="Resume the music")
async def resume(ctx):
    voice_client = ctx.guild.voice_client
    if voice_client and voice_client.is_paused():
        voice_client.resume()
        await ctx.respond("Music resumed.")
    else:
        await ctx.respond("No song is currently paused.")
@resume.error
async def resume_error(ctx, error):
    await ctx.respond(f"An error occurred while trying to resume the music: {error}")
    raise error

#queue command
@bot.slash_command(guild_ids=servers, name="queue", description="Show the queue")
async def queue(ctx):
    if song_queue:
        queue_list = ""
        for i, song in enumerate(song_queue):
            queue_list += f"{i + 1}. {song}\n"
        await ctx.respond(f"Queue:\n{queue_list}")
    else:
        await ctx.respond("The queue is empty.")

#anime commands



@bot.event
async def on_ready():
    for file in os.listdir():
                if file.endswith('.mp3'):
                    os.remove(file)
    print("Ready!")

dotenv.load_dotenv()

bot.run(os.getenv("TOKEN"))
