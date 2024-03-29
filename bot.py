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
import aiohttp
import traceback
import datetime as dt

admin_roles = [1173725609382400106, 1173729989670223882]  # Hier kun je de gewenste admin-role ID's plaatsen
muted_role = 1197094790379089971  # Hier kun je de gewenste muted-role ID plaatsen
log_channel_id = 1173725610309341401 # Hier kun je de gewenste log-channel ID plaatsen

bot = discord.Bot()

servers = [1173725609382400101] # Hier kun je de gewenste server ID's plaatsen

#Administrator commands

#banlist command

@bot.slash_command(guild_ids=servers, name="banlist", description="Get list of banned users")  #commando voor de banlist
@commands.has_permissions(ban_members=True) #check of gebruiker de juiste permissies heeft
async def banlist(ctx): # context van het commando
    await ctx.defer() #bot reageert later
    embed = discord.Embed(title="Banned Users", description="List of banned users", color=0x00ff00, timestamp=datetime.utcnow() + timedelta(hours=1)) #embed met titel, beschrijving, kleur en tijd
    async for entry in ctx.guild.bans(): #loop door de gebande gebruikers
        if len(embed.fields) >= 25: #als er meer dan 25 gebande gebruikers zijn, stop de loop
            break
        if len(embed) > 5900: #als de embed groter is dan 5900 karakters, stop de loop
            embed.add_field(name="Banned Users", value="Too many users to display")
        else: #voeg de gebande gebruiker toe aan de embed
            embed.add_field(name=f"ban", value = f"Username: {entry.user.name}#{entry.user.discriminator}\nID: {entry.user.id}\nReason: {entry.reason}")
            
    await ctx.respond(embed=embed) #stuur de embed
    
    
#unban command

@bot.slash_command(guild_ids=servers, name="unban", description="Unban a user") #commando voor het unbannen van een gebruiker
@commands.has_permissions(ban_members=True) #check of gebruiker de juiste permissies heeft
async def unban(ctx, user: str = discord.Option(name="user", description="The user to unban", required=True)): #context van het commando en de gebruiker die je wilt unbannen
    await ctx.defer() #bot reageert later
    try: #probeer de gebruiker te unbannen
        user_id = int(user) 
    except ValueError: #Error als de gebruiker id ongeldig is
        await ctx.send("Please provide a valid user ID.")  
        return
    
    member = await bot.fetch_user(user_id) 
    await ctx.guild.unban(member) 
    await ctx.respond(f"Unbanned {member.mention}") 
    log_channel = bot.get_channel(log_channel_id) #log aanmaken dat er een gebruiker is unbanned
    await log_channel.send(f"{member.mention} has been unbanned by {ctx.author.mention} ")
@unban.error #error als de gebruiker niet unbanned kan worden
async def on_application_command_error(ctx, error):
    if isinstance(error, MissingPermissions): #als de gebruiker niet de juiste permissies heeft
        await ctx.respond("You don't have the required permissions to run this command.")
    else: #als er een andere error is
        await ctx.respond(f"Something went wrong, I couldn't unban this member or the member isn't banned. Error: {error}")
        raise error

#ban command

@bot.slash_command(guild_ids=servers, name="ban", description="Ban a user") #commando voor het bannen van een gebruiker
@commands.has_permissions(ban_members=True) #check of gebruiker de juiste permissies heeft
async def ban(ctx, member: Option(discord.Member, description="The member to ban"), reason: Option(str, description="why?", required=False)): # type: ignore context van het commando en de gebruiker die je wilt bannen en de reden
    if member.id == ctx.author.id: #als de gebruiker zichzelf probeert te bannen
        await ctx.respond("You can't ban yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator: #als de gebruiker een admin probeert te bannen
        await ctx.respond("You can't ban an admin!")
        return
    else: #bannen van de gebruiker
        if reason is None: #als er geen reden is gegeven
            reason = f"No reason provided by {ctx.author.name}"
        await member.send(f"You have been banned from {ctx.guild.name} for {reason}")
        await ctx.guild.ban(member, reason=reason)
        await ctx.respond(f"You have banned {member.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been banned by {ctx.author.mention} for {reason}")
@ban.error #error als de gebruiker niet gebanned kan worden
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions): #als de gebruiker niet de juiste permissies heeft
        await ctx.respond("You don't have the required permissions to run this command.")
    else: #als er een andere error is
        await ctx.respond(f"Something went wrong, I couldn't ban this member. Error: {error}")
        raise error
        
    
#kick command

@bot.slash_command(guild_ids=servers, name="kick", description="Kick a user") #commando voor het kicken van een gebruiker
@commands.has_permissions(kick_members=True) #check of gebruiker de juiste permissies heeft
async def kick(ctx, member: Option(discord.Member, description="The member to ban"), reason: Option(str, description="why?", required=False)):  # type: ignore context van het commando en de gebruiker die je wilt kicken en de reden
    if member.id == ctx.author.id: #als de gebruiker zichzelf probeert te kicken
        await ctx.respond("You can't kick yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator: #als de gebruiker een admin probeert te kicken
        await ctx.respond("You can't kick an admin!")
        return
    else: #kicken van de gebruiker
        if reason is None: #als er geen reden is gegeven
            reason = f"No reason provided by {ctx.author.name}"
        await member.send(f"You have been kicked from {ctx.guild.name} for {reason}")
        await ctx.guild.kick(member, reason=reason)
        await ctx.respond(f"You have kicked {member.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been kicked by {ctx.author.mention} for {reason}")
@ban.error #error als de gebruiker niet gekicked kan worden
async def ban_error(ctx, error):
    if isinstance(error, MissingPermissions): #als de gebruiker niet de juiste permissies heeft
        await ctx.respond("You don't have the required permissions to run this command.")
    else: #als er een andere error is
        await ctx.respond(f"Something went wrong, I couldn't ban this member. Error: {error}")
        raise error

#mute command
@bot.slash_command(guild_ids=servers, name="mute", description="Mute a user")  #commando voor het muten van een gebruiker
@commands.has_permissions(manage_roles=True) #check of gebruiker de juiste permissies heeft
async def mute(ctx, member: Option(discord.Member, description="The member to mute"), reason: Option(str, description="why?", required=False)): # type: ignore context van het commando en de gebruiker die je wilt muten en de reden
    if member.id == ctx.author.id: #als de gebruiker zichzelf probeert te muten
        await ctx.respond("You can't mute yourself!")
        return
    elif ctx.guild.get_member(member.id) and ctx.guild.get_member(member.id).guild_permissions.administrator: #als de gebruiker een admin probeert te muten
        await ctx.respond("You can't mute an admin!")
        return
    if discord.utils.get(member.roles, id=muted_role) is not None: #als de gebruiker al gemuted is
        await ctx.respond(f"{member.mention} is already muted.")
        return
    else: #muten van de gebruiker
        if reason is None: #als er geen reden is gegeven
            reason = f"No reason provided by {ctx.author.name}"
        await member.send(f"You have been muted in {ctx.guild.name} for {reason}")
        await member.add_roles(ctx.guild.get_role(muted_role))
        await ctx.respond(f"you have muted {member.mention} for {reason}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been muted by {ctx.author.mention} for {reason}")
@mute.error #error als de gebruiker niet gemuted kan worden
async def mute_error(ctx, error):
    if isinstance(error, MissingPermissions):  #als de gebruiker niet de juiste permissies heeft
        await ctx.respond("You don't have the required permissions to run this command.")
    else: #als er een andere error is
        await ctx.respond(f"Something went wrong, I couldn't mute this member. Error: {error}")
        raise error

#unmute command
@bot.slash_command(guild_ids=servers, name="unmute", description="Unmute a user") #commando voor het unmuten van een gebruiker
@commands.has_permissions(manage_roles=True) #check of gebruiker de juiste permissies heeft
async def unmute(ctx, member: Option(discord.Member, description="The member to unmute")): # type: ignore context van het commando en de gebruiker die je wilt unmuten
    if discord.utils.get(member.roles, id=muted_role) is not None: #als de gebruiker gemuted is unnmuten
        
        await member.remove_roles(ctx.guild.get_role(muted_role))
        await ctx.respond(f"You have unmuted {member.mention}")
        log_channel = bot.get_channel(log_channel_id)
        await log_channel.send(f"{member.mention} has been unmuted by {ctx.author.mention}")
    else: #als de gebruiker niet gemuted is
        await ctx.respond(f"{member.mention} is not muted.")
@unmute.error #error als de gebruiker niet ungemuted kan worden
async def unmute_error(ctx, error):
    if isinstance(error, MissingPermissions): #als de gebruiker niet de juiste permissies heeft
        await ctx.respond("You don't have the required permissions to run this command.")
    else: #als er een andere error is
        await ctx.respond(f"Something went wrong, I couldn't unmute this member. Error: {error}")
        raise error

#clear command
@bot.slash_command(guild_ids=servers, name="clear", description="Clear messages") #commando voor het clearen van berichten
@commands.has_permissions(manage_messages=True) #check of gebruiker de juiste permissies heeft
async def clear(ctx, amount: Option(int, description="The amount of messages to clear")): # type: ignore context van het commando en het aantal berichten dat je wilt clearen
    await ctx.channel.purge(limit=amount) #clearen van de berichten
    await ctx.respond(f"{amount} messages have been cleared")
@clear.error #error als de berichten niet gecleared kunnen worden
async def clear_error(ctx, error):
    if isinstance(error, MissingPermissions): #als de gebruiker niet de juiste permissies heeft
        await ctx.respond("You don't have the required permissions to run this command.")
    else: #als er een andere error is
        await ctx.respond(f"Something went wrong, I couldn't clear messages. Error: {error}")
        raise error

#music commands


# Queue to hold songs
song_queue = deque()

@bot.slash_command(guild_ids=servers, name="play", description="Play a song") #commando voor het afspelen van een nummer
async def play(ctx, song: str): #context van het commando en het nummer dat je wilt afspelen
    voice_channel = ctx.author.voice.channel #check of de gebruiker in een voice channel zit
    if voice_channel is None: #als de gebruiker niet in een voice channel zit
        await ctx.respond("You are not in a voice channel.")
        return
    
    if "list=" in song: #check of de gebruiker een playlist probeert af te spelen
        await ctx.respond("I can't play playlists yet, only single songs.")
        return
    voice_client = ctx.guild.voice_client #check of de bot al in een voice channel zit

    if voice_client and voice_client.is_playing(): #als de bot al een nummer aan het afspelen is
        song_queue.append(song) #nummer toevoegen aan de queue
        await ctx.respond(f"{song} has been added to the queue.")
        return

    if voice_client is None: #als de bot niet in een voice channel zit
        voice_client = await voice_channel.connect()

    await ctx.defer() #bot reageert later

    await play_song(ctx, song) #nummer afspelen

async def play_song(ctx, song): #nummer afspelen context
    ydl_opts = { #youtube downloader opties directe download
        'format': 'bestaudio/best', # audio format
        'outtmpl': 'tempsong',  # filename
        'postprocessors': [{  # postprocessors
            'key': 'FFmpegExtractAudio', # ffmpeg extract audio
            'preferredcodec': 'mp3', # codec voorkeur
            
        }], 
        'default_search': 'ytsearch', # standaard zoekopdracht
        'extractor_args': { #extractor argumenten
            'youtube': { 
                'default_search': 'auto', # standaard zoekopdracht
                'format': 'bestaudio/best', # audio format
                'postprocessors': [{ # postprocessors
                    'key': 'FFmpegExtractAudio', # ffmpeg extract audio
                    'preferredcodec': 'mp3', # codec voorkeur

                }],
            },
        },
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl: #youtube downloader
        try: #probeer het nummer te downloaden
            info = ydl.extract_info(song, download=True)
            
        except yt_dlp.DownloadError as e: #error als het nummer niet gedownload kan worden
            await ctx.respond(f"An error occurred while trying to play the song: {e}")
            return

    try: #probeer het nummer af te spelen
        voice_client = ctx.guild.voice_client
        voice_client.play(discord.FFmpegPCMAudio('tempsong.mp3'), after=lambda e: play_next(ctx))
        await ctx.respond(f"Now playing: {song}")
    except Exception as e: #error als het nummer niet afgespeeld kan worden
        await ctx.respond(f"An error occurred while playing the song: {e}")
        print(f"Error occurred while playing the song: {e}")

def play_next(ctx): #volgende nummer afspelen
    voice_client = ctx.guild.voice_client #check of de bot in een voice channel zit
    if song_queue: #als er nog nummers in de queue zitten
        next_song = song_queue.popleft()
        asyncio.run(play_song(ctx, next_song))
    else: #als er geen nummers meer in de queue zitten
        os.remove('tempsong.mp3')

# Skip command
@bot.slash_command(guild_ids=servers, name="skip", description="Skip the current song") #commando voor het skippen van een nummer
async def skip(ctx): #context van het commando
    voice_client = ctx.guild.voice_client #check of de bot in een voice channel zit
    if voice_client and voice_client.is_playing(): #check of er een nummer aan het afspelen is en skip het nummer
        voice_client.stop() 
        await ctx.respond("Song skipped.")
    else: #als er geen nummer aan het afspelen is
        await ctx.respond("No song is currently playing.")
@skip.error #error als het nummer niet geskipt kan worden
async def skip_error(ctx, error): 
    await ctx.respond(f"An error occurred while trying to skip the song: {error}")
    raise error

# Stop command
@bot.slash_command(guild_ids=servers, name="stop", description="Stop the music")   #commando voor het stoppen van de muziek
async def stop(ctx): #context van het commando
    voice_client = ctx.guild.voice_client #check of de bot in een voice channel zit
    if voice_client and voice_client.is_playing(): #stop de muziek als de bot aan het afspelen is
        await ctx.respond("Music stopped.")
        voice_client.stop()
        await voice_client.disconnect()
        
    else: #als er geen muziek aan het afspelen is
        await ctx.respond("No song is currently playing.")
@stop.error #error als de muziek niet gestopt kan worden
async def stop_error(ctx, error): 
    await ctx.respond(f"An error occurred while trying to stop the music: {error}")
    raise error

# Pause command
@bot.slash_command(guild_ids=servers, name="pause", description="Pause the music")  #commando voor het pauzeren van de muziek
async def pause(ctx): #context van het commando
    voice_client = ctx.guild.voice_client #check of de bot in een voice channel zit
    if voice_client and voice_client.is_playing(): #pauzeer de muziek als de bot aan het afspelen is
        voice_client.pause()
        await ctx.respond("Music paused.")
    else: #als er geen muziek aan het afspelen is
        await ctx.respond("No song is currently playing.")
@pause.error #error als de muziek niet gepauzeerd kan worden
async def pause_error(ctx, error):
    await ctx.respond(f"An error occurred while trying to pause the music: {error}")
    raise error

# Resume command
@bot.slash_command(guild_ids=servers, name="resume", description="Resume the music") #commando voor het hervatten van de muziek
async def resume(ctx): #context van het commando
    voice_client = ctx.guild.voice_client #check of de bot in een voice channel zit
    if voice_client and voice_client.is_paused(): #hervat de muziek als de bot op pauze is
        voice_client.resume()
        await ctx.respond("Music resumed.")
    else: #als er geen muziek op pauze staat
        await ctx.respond("No song is currently paused.")
@resume.error #error als de muziek niet hervat kan worden
async def resume_error(ctx, error): 
    await ctx.respond(f"An error occurred while trying to resume the music: {error}")
    raise error

#queue command
@bot.slash_command(guild_ids=servers, name="queue", description="Show the queue") #commando voor het weergeven van de queue
async def queue(ctx): #context van het commando
    if song_queue: #als er nummers in de queue zitten laat queue zien
        queue_list = ""
        for i, song in enumerate(song_queue):
            queue_list += f"{i + 1}. {song}\n"
        await ctx.respond(f"Queue:\n{queue_list}")
    else: #als er geen nummers in de queue zitten
        await ctx.respond("The queue is empty.")

#anime commands


# anime image reversal command


trace_url = 'https://api.trace.moe/search' # Trace Moe API URL

@bot.slash_command(guild_ids=servers, name="anime-image", description="Find information about an anime from an image") #commando voor het zoeken van informatie over een anime van een afbeelding
async def anime(ctx): #context van het commando
    await ctx.respond("Please upload the anime image you want to search for.") #vraag de gebruiker om een afbeelding te uploaden

    def check(message): #check of de gebruiker een afbeelding heeft geupload
        return message.author == ctx.author and message.attachments

    image_path = None  

    try: #probeer de afbeelding te vinden
        message = await bot.wait_for('message', check=check, timeout=60)
        image = message.attachments[0]

        # donwload de afbeelding
        image_path = f"temp_image_{ctx.interaction.id}.png"
        await image.save(image_path)

        # stuur de afbeelding naar de Trace Moe API
        async with aiohttp.ClientSession() as session: #maak een sessie aan
            with open(image_path, 'rb') as file: #open de afbeelding
                async with session.post(f"{trace_url}?anilistInfo", data={'image': file}) as resp: #post de afbeelding naar de API
                    if resp.status == 200: #check of de API de afbeelding heeft ontvangen
                        async def fmtTime(timestamp): #format de tijd
                            return dt.datetime.utcfromtimestamp(timestamp).strftime("%H:%M:%S UTC") 

                        anime_info = await resp.json() #krijg de informatie van de anime

                        
                        if anime_info.get('result') and anime_info['result'][0].get('anilist'): #check of de anime is gevonden in de afbeelding en haal de informatie op
                            data = anime_info['result'][0] 
                            at = await fmtTime(data["from"]) 
                            anilist_id = data["anilist"]["id"] 
                            link = f"https://anilist.co/anime/{anilist_id}" 
                            title_romaji = data["anilist"]["title"]["romaji"] 
                            episode = data["episode"] 
                            
                            # maak een embed met de informatie van de anime
                            embed = discord.Embed(title="Anime Information", color=discord.Color(0xFFB6C1))
                            embed.add_field(name="Anime", value=title_romaji, inline=False)
                            embed.add_field(name="Episode", value=episode, inline=False)
                            embed.add_field(name="At", value=at, inline=False)
                            embed.add_field(name="Link", value=f"[Anilist]({link})", inline=False)
                            
                            await ctx.respond(embed=embed) #stuur de embed
                        else: #als er geen anime is gevonden in de afbeelding
                            await ctx.respond("No anime found in the image.")
                    else: #als de API de afbeelding niet heeft ontvangen
                        await ctx.respond(f"Failed to retrieve anime information. Status code: {resp.status}")

    except asyncio.TimeoutError: #error als de gebruiker geen afbeelding heeft geupload in de tijdslimiet
        await ctx.respond("No image provided within the time limit.")
    except Exception as e: #error als er een andere error is
        traceback.print_exc() 
        await ctx.respond(f"An error occurred: {str(e)}")
    finally:
        if image_path and os.path.exists(image_path): #verwijder de afbeelding van de server
            os.remove(image_path)
        

# help commando
@bot.slash_command(guild_ids=servers, name="help", description="Get help with commands") #commando voor het weergeven van de commando's
async def help(ctx): #context van het commando
    #zet de commando's in een embed
    embed = discord.Embed(title="Commands", description="List of commands", color=0x00ff00)
    embed.add_field(name="/banlist", value="Get list of banned users", inline=False)
    embed.add_field(name="/unban", value="Unban a user", inline=False)
    embed.add_field(name="/ban", value="Ban a user", inline=False)
    embed.add_field(name="/kick", value="Kick a user", inline=False)
    embed.add_field(name="/mute", value="Mute a user", inline=False)
    embed.add_field(name="/unmute", value="Unmute a user", inline=False)
    embed.add_field(name="/clear", value="Clear messages", inline=False)
    embed.add_field(name="/play", value="Play a song", inline=False)
    embed.add_field(name="/skip", value="Skip the current song", inline=False)
    embed.add_field(name="/stop", value="Stop the music", inline=False)
    embed.add_field(name="/pause", value="Pause the music", inline=False)
    embed.add_field(name="/resume", value="Resume the music", inline=False)
    embed.add_field(name="/queue", value="Show the queue", inline=False)
    embed.add_field(name="/anime-image", value="Find information about an anime from an image", inline=False)
    await ctx.respond(embed=embed) #stuur de embed



@bot.event #als de bot klaar is met laden
async def on_ready():
    for file in os.listdir(): #verwijder de tijdelijke bestanden
                if file.endswith('.mp3'):
                    os.remove(file)
    print("Ready!") #print dat de bot klaar is

dotenv.load_dotenv() #laad de .env file

bot.run(os.getenv("TOKEN")) #run de bot
