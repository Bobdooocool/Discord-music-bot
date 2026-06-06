import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.music_manager import MusicManager, YouTubeManager
from utils.voice_manager import VoiceManager

class MusicCommands(commands.Cog):
    """Advanced music playback commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_manager = MusicManager()
        self.voice_manager = VoiceManager()
        self.now_playing: dict = {}
    
    @app_commands.command(name="play", description="Search and play a song from YouTube")
    @app_commands.describe(query="Song name or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        """Search and play a song"""
        await interaction.response.defer()
        
        try:
            # Check if user is in a voice channel
            if not interaction.user.voice or not interaction.user.voice.channel:
                embed = discord.Embed(
                    title="❌ Not in Voice",
                    description="You must be in a voice channel to play music!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            voice_channel = interaction.user.voice.channel
            guild_id = interaction.guild.id
            
            # Show searching status
            search_embed = discord.Embed(
                title="🔍 Searching...",
                description=f"Looking for: **{query}**",
                color=discord.Color.blurple()
            )
            await interaction.followup.send(embed=search_embed)
            
            # Search for the track
            track_info = YouTubeManager.search(query)
            
            if not track_info:
                embed = discord.Embed(
                    title="❌ Not Found",
                    description=f"Could not find: **{query}**",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Connect to voice if not already connected
            voice_client = interaction.guild.voice_client
            if not voice_client:
                try:
                    voice_client = await voice_channel.connect()
                except Exception as e:
                    embed = discord.Embed(
                        title="❌ Connection Failed",
                        description=f"Could not connect to voice: {e}",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed)
                    return
            
            # Add to queue and get position
            position = self.music_manager.add_to_queue(guild_id, track_info)
            
            # Show added embed
            embed = discord.Embed(
                title="✅ Added to Queue",
                color=discord.Color.green()
            )
            embed.add_field(name="🎵 Song", value=f"**{track_info['title']}**", inline=False)
            embed.add_field(name="👤 Artist", value=track_info['uploader'], inline=True)
            embed.add_field(name="⏱️ Duration", value=f"{track_info['duration']}s", inline=True)
            embed.add_field(name="📍 Position", value=f"#{position} in queue", inline=False)
            
            if track_info['thumbnail']:
                embed.set_thumbnail(url=track_info['thumbnail'])
            
            await interaction.followup.send(embed=embed)
            
            # If nothing is playing, start playing
            if not voice_client.is_playing():
                await self._play_next(interaction.guild)
        
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
            print(f"Play command error: {e}")
    
    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        """Pause playback"""
        await interaction.response.defer()
        
        try:
            voice_client = interaction.guild.voice_client
            
            if not voice_client or not voice_client.is_playing():
                embed = discord.Embed(
                    title="❌ Nothing Playing",
                    description="There's no music playing right now!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            voice_client.pause()
            
            current = self.music_manager.get_current(interaction.guild.id)
            embed = discord.Embed(
                title="⏸️ Paused",
                description=f"**{current['title']}** has been paused",
                color=discord.Color.yellow()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="resume", description="Resume the current song")
    async def resume(self, interaction: discord.Interaction):
        """Resume playback"""
        await interaction.response.defer()
        
        try:
            voice_client = interaction.guild.voice_client
            
            if not voice_client or not voice_client.is_paused():
                embed = discord.Embed(
                    title="❌ Not Paused",
                    description="Nothing is paused right now!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            voice_client.resume()
            
            current = self.music_manager.get_current(interaction.guild.id)
            embed = discord.Embed(
                title="▶️ Resumed",
                description=f"**{current['title']}** has been resumed",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="skip", description="Skip to the next song")
    async def skip(self, interaction: discord.Interaction):
        """Skip to next track"""
        await interaction.response.defer()
        
        try:
            voice_client = interaction.guild.voice_client
            
            if not voice_client:
                embed = discord.Embed(
                    title="❌ Not Connected",
                    description="Bot is not connected to voice!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            if voice_client.is_playing():
                voice_client.stop()
            
            embed = discord.Embed(
                title="⏭️ Skipped",
                description="Skipping to next song...",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
            
            await self._play_next(interaction.guild)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="stop", description="Stop music and disconnect")
    async def stop(self, interaction: discord.Interaction):
        """Stop playback and disconnect"""
        await interaction.response.defer()
        
        try:
            voice_client = interaction.guild.voice_client
            
            if not voice_client:
                embed = discord.Embed(
                    title="❌ Not Connected",
                    description="Bot is not connected to voice!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            voice_client.stop()
            await voice_client.disconnect()
            self.music_manager.clear_queue(interaction.guild.id)
            
            embed = discord.Embed(
                title="⏹️ Stopped",
                description="Music has been stopped and bot disconnected",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="queue", description="View the current music queue")
    async def queue(self, interaction: discord.Interaction):
        """Show the queue"""
        await interaction.response.defer()
        
        try:
            queue = self.music_manager.get_queue(interaction.guild.id)
            current = self.music_manager.get_current(interaction.guild.id)
            
            embed = discord.Embed(
                title="🎵 Music Queue",
                color=discord.Color.blurple()
            )
            
            if current:
                embed.add_field(
                    name="🎶 Now Playing",
                    value=f"**{current['title']}**\n👤 {current['uploader']}",
                    inline=False
                )
            
            if not queue:
                embed.add_field(
                    name="📋 Upcoming",
                    value="Queue is empty!",
                    inline=False
                )
            else:
                queue_text = ""
                for i, track in enumerate(queue[:10], 1):
                    queue_text += f"{i}. **{track['title']}** ({track['duration']}s)\n"
                
                if len(queue) > 10:
                    queue_text += f"\n... and {len(queue) - 10} more songs"
                
                embed.add_field(
                    name=f"📋 Upcoming ({len(queue)} songs)",
                    value=queue_text,
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    async def _play_next(self, guild: discord.Guild):
        """Play the next track in queue"""
        try:
            queue = self.music_manager.get_queue(guild.id)
            voice_client = guild.voice_client
            
            if not voice_client or not queue:
                return
            
            track = queue.pop(0)
            self.music_manager.set_current(guild.id, track)
            
            # Get audio URL
            audio_url = YouTubeManager.get_audio_url(track['url'])
            
            if not audio_url:
                # Try next track if this one fails
                await self._play_next(guild)
                return
            
            # Create FFmpeg source
            try:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(
                        audio_url,
                        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                        options="-vn -q:a 9 -acodec libopus -f s16le -ac 2 -ar 48000"
                    )
                )
                
                # Play the source
                def after_playback(error):
                    if error:
                        print(f"Playback error: {error}")
                    # Schedule next track
                    asyncio.run_coroutine_threadsafe(self._play_next(guild), self.bot.loop)
                
                voice_client.play(source, after=after_playback)
            
            except Exception as e:
                print(f"Error creating audio source: {e}")
                await self._play_next(guild)
        
        except Exception as e:
            print(f"Error in _play_next: {e}")

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))
