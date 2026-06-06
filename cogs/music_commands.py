import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.music_manager import MusicManager, YouTubeManager, PlaylistManager
from utils.voice_manager import VoiceManager

class MusicCommands(commands.Cog):
    """Music playback commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_manager = MusicManager()
        self.playlist_manager = PlaylistManager()
        self.voice_manager = VoiceManager()
        self.playing: dict = {}
    
    @app_commands.command(name="play", description="Play a song from YouTube")
    @app_commands.describe(query="Song name or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        """Play a song"""
        await interaction.response.defer()
        
        try:
            # Check if user is in a voice channel
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send("❌ You must be in a voice channel!")
                return
            
            voice_channel = interaction.user.voice.channel
            
            # Search for the track
            embed = discord.Embed(
                title="🔍 Searching...",
                description=f"Looking for: {query}",
                color=discord.Color.blurple()
            )
            await interaction.followup.send(embed=embed)
            
            track_info = YouTubeManager.search(query)
            
            if not track_info:
                await interaction.followup.send("❌ Could not find that song!")
                return
            
            # Connect to voice if not already connected
            guild_id = interaction.guild.id
            if not interaction.guild.voice_client:
                try:
                    await voice_channel.connect()
                except Exception as e:
                    await interaction.followup.send(f"❌ Could not connect to voice: {e}")
                    return
            
            # Add to queue
            self.music_manager.add_to_queue(guild_id, track_info)
            
            # Create embed for the track
            embed = discord.Embed(
                title="🎵 Added to Queue",
                description=f"**{track_info['title']}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Uploader", value=track_info['uploader'], inline=False)
            embed.add_field(name="Duration", value=f"{track_info['duration']} seconds", inline=False)
            
            if track_info['thumbnail']:
                embed.set_thumbnail(url=track_info['thumbnail'])
            
            await interaction.followup.send(embed=embed)
            
            # Play if nothing is playing
            if not interaction.guild.voice_client.is_playing():
                await self._play_next(interaction.guild)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        """Pause playback"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild.voice_client or not interaction.guild.voice_client.is_playing():
                await interaction.followup.send("❌ Nothing is playing!")
                return
            
            interaction.guild.voice_client.pause()
            embed = discord.Embed(
                title="⏸️ Paused",
                description="Music has been paused",
                color=discord.Color.yellow()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="resume", description="Resume the current song")
    async def resume(self, interaction: discord.Interaction):
        """Resume playback"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild.voice_client or not interaction.guild.voice_client.is_paused():
                await interaction.followup.send("❌ Nothing is paused!")
                return
            
            interaction.guild.voice_client.resume()
            embed = discord.Embed(
                title="▶️ Resumed",
                description="Music has been resumed",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="skip", description="Skip to the next song")
    async def skip(self, interaction: discord.Interaction):
        """Skip to next track"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild.voice_client:
                await interaction.followup.send("❌ Not connected to voice!")
                return
            
            next_track = self.music_manager.skip_track(interaction.guild.id)
            
            if interaction.guild.voice_client.is_playing():
                interaction.guild.voice_client.stop()
            
            embed = discord.Embed(
                title="⏭️ Skipped",
                description="Skipping to next song...",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
            
            await self._play_next(interaction.guild)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="stop", description="Stop the music and disconnect")
    async def stop(self, interaction: discord.Interaction):
        """Stop playback and disconnect"""
        await interaction.response.defer()
        
        try:
            if not interaction.guild.voice_client:
                await interaction.followup.send("❌ Not connected to voice!")
                return
            
            interaction.guild.voice_client.stop()
            await interaction.guild.voice_client.disconnect()
            self.music_manager.clear_queue(interaction.guild.id)
            
            embed = discord.Embed(
                title="⏹️ Stopped",
                description="Music has been stopped and disconnected",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="queue", description="View the current queue")
    async def queue(self, interaction: discord.Interaction):
        """Show the queue"""
        await interaction.response.defer()
        
        try:
            queue = self.music_manager.get_queue(interaction.guild.id)
            
            if not queue:
                await interaction.followup.send("❌ Queue is empty!")
                return
            
            embed = discord.Embed(
                title="🎵 Queue",
                color=discord.Color.blurple()
            )
            
            for i, track in enumerate(queue[:10], 1):
                embed.add_field(
                    name=f"{i}. {track['title']}",
                    value=f"Duration: {track['duration']}s",
                    inline=False
                )
            
            if len(queue) > 10:
                embed.add_field(
                    name="...",
                    value=f"And {len(queue) - 10} more songs",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    async def _play_next(self, guild: discord.Guild):
        """Play the next track in queue"""
        try:
            queue = self.music_manager.get_queue(guild.id)
            
            if not queue:
                return
            
            track = queue.pop(0)
            self.music_manager.set_current(guild.id, track)
            
            audio_url = YouTubeManager.get_audio_url(track['url'])
            
            if not audio_url:
                await self._play_next(guild)
                return
            
            source = discord.PCMVolumeTransformer(
                discord.FFmpegPCMAudio(audio_url, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options="-vn")
            )
            
            guild.voice_client.play(
                source,
                after=lambda e: asyncio.run_coroutine_threadsafe(self._play_next(guild), self.bot.loop)
            )
        
        except Exception as e:
            print(f"Error playing next track: {e}")

async def setup(bot):
    await bot.add_cog(MusicCommands(bot))
