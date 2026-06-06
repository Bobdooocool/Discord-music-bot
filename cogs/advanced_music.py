import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.music_manager import MusicManager, YouTubeManager

class MusicControlPanel(discord.ui.View):
    """Advanced music control panel with buttons and dropdowns"""
    
    def __init__(self, bot, guild_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.music_manager = MusicManager()
    
    @discord.ui.button(label="⏸️ Pause", style=discord.ButtonStyle.gray)
    async def pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.followup.send("⏸️ Music paused", ephemeral=True)
        else:
            await interaction.followup.send("❌ Nothing is playing", ephemeral=True)
    
    @discord.ui.button(label="▶️ Resume", style=discord.ButtonStyle.gray)
    async def resume_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await interaction.followup.send("▶️ Music resumed", ephemeral=True)
        else:
            await interaction.followup.send("❌ Nothing is paused", ephemeral=True)
    
    @discord.ui.button(label="⏭️ Skip", style=discord.ButtonStyle.gray)
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.followup.send("⏭️ Skipped to next song", ephemeral=True)
        else:
            await interaction.followup.send("❌ Nothing is playing", ephemeral=True)
    
    @discord.ui.button(label="⏹️ Stop", style=discord.ButtonStyle.danger)
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        voice_client = interaction.guild.voice_client
        if voice_client:
            voice_client.stop()
            await voice_client.disconnect()
            await interaction.followup.send("⏹️ Music stopped and disconnected", ephemeral=True)
        else:
            await interaction.followup.send("❌ Bot is not connected", ephemeral=True)
    
    @discord.ui.button(label="📋 Queue", style=discord.ButtonStyle.blurple)
    async def queue_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        queue = self.music_manager.get_queue(self.guild_id)
        current = self.music_manager.get_current(self.guild_id)
        
        embed = discord.Embed(title="🎵 Queue", color=discord.Color.blurple())
        
        if current:
            embed.add_field(name="🎶 Now Playing", value=f"**{current['title']}**", inline=False)
        
        if queue:
            queue_text = ""
            for i, track in enumerate(queue[:5], 1):
                queue_text += f"{i}. {track['title']}\n"
            if len(queue) > 5:
                queue_text += f"... and {len(queue) - 5} more"
            embed.add_field(name="📋 Upcoming", value=queue_text, inline=False)
        else:
            embed.add_field(name="📋 Upcoming", value="Queue is empty", inline=False)
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class AdvancedMusicCommands(commands.Cog):
    """Advanced music commands with dropdown menus"""
    
    def __init__(self, bot):
        self.bot = bot
        self.music_manager = MusicManager()
    
    @app_commands.command(name="control", description="Show music control panel")
    async def show_control_panel(self, interaction: discord.Interaction):
        """Show the control panel with buttons"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🎛️ Music Control Panel",
                description="Control the music with these buttons:",
                color=discord.Color.blurple()
            )
            embed.add_field(name="⏸️ Pause", value="Pause the current song", inline=True)
            embed.add_field(name="▶️ Resume", value="Resume the song", inline=True)
            embed.add_field(name="⏭️ Skip", value="Skip to next song", inline=True)
            embed.add_field(name="⏹️ Stop", value="Stop music", inline=True)
            embed.add_field(name="📋 Queue", value="View queue", inline=True)
            
            await interaction.followup.send(
                embed=embed,
                view=MusicControlPanel(self.bot, interaction.guild.id)
            )
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="playsearch", description="Search and play with advanced options")
    @app_commands.describe(query="Song to search for")
    async def play_search(self, interaction: discord.Interaction, query: str):
        """Advanced search with results selection"""
        await interaction.response.defer()
        
        try:
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send("❌ You must be in a voice channel!")
                return
            
            voice_channel = interaction.user.voice.channel
            guild_id = interaction.guild.id
            
            # Search
            embed = discord.Embed(
                title="🔍 Searching...",
                description=f"Looking for: **{query}**",
                color=discord.Color.blurple()
            )
            await interaction.followup.send(embed=embed)
            
            track_info = YouTubeManager.search(query)
            
            if not track_info:
                await interaction.followup.send("❌ No results found!")
                return
            
            # Connect
            voice_client = interaction.guild.voice_client
            if not voice_client:
                try:
                    voice_client = await voice_channel.connect()
                except Exception as e:
                    await interaction.followup.send(f"❌ Could not connect: {e}")
                    return
            
            # Add to queue
            position = self.music_manager.add_to_queue(guild_id, track_info)
            
            # Show result
            embed = discord.Embed(
                title="✅ Added to Queue",
                color=discord.Color.green()
            )
            embed.add_field(name="🎵 Song", value=track_info['title'], inline=False)
            embed.add_field(name="👤 Artist", value=track_info['uploader'], inline=True)
            embed.add_field(name="⏱️ Duration", value=f"{track_info['duration']}s", inline=True)
            embed.add_field(name="📍 Position", value=f"#{position}", inline=False)
            
            if track_info['thumbnail']:
                embed.set_thumbnail(url=track_info['thumbnail'])
            
            await interaction.followup.send(embed=embed)
            
            if not voice_client.is_playing():
                await self._play_next(interaction.guild)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    async def _play_next(self, guild: discord.Guild):
        """Play next track"""
        try:
            queue = self.music_manager.get_queue(guild.id)
            voice_client = guild.voice_client
            
            if not voice_client or not queue:
                return
            
            track = queue.pop(0)
            self.music_manager.set_current(guild.id, track)
            
            audio_url = YouTubeManager.get_audio_url(track['url'])
            
            if not audio_url:
                await self._play_next(guild)
                return
            
            try:
                source = discord.PCMVolumeTransformer(
                    discord.FFmpegPCMAudio(
                        audio_url,
                        before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                        options="-vn"
                    )
                )
                
                def after_playback(error):
                    if error:
                        print(f"Playback error: {error}")
                    asyncio.run_coroutine_threadsafe(self._play_next(guild), self.bot.loop)
                
                voice_client.play(source, after=after_playback)
            
            except Exception as e:
                print(f"Error: {e}")
                await self._play_next(guild)
        
        except Exception as e:
            print(f"Play next error: {e}")

async def setup(bot):
    await bot.add_cog(AdvancedMusicCommands(bot))
