import discord
from discord.ext import commands
from discord import app_commands
from utils.music_manager import PlaylistManager, YouTubeManager

class PlaylistCommands(commands.Cog):
    """Playlist management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.playlist_manager = PlaylistManager()
    
    @app_commands.command(name="playlist_create", description="Create a new playlist")
    @app_commands.describe(name="Playlist name")
    async def create_playlist(self, interaction: discord.Interaction, name: str):
        """Create a new playlist"""
        await interaction.response.defer()
        
        try:
            if self.playlist_manager.create_playlist(interaction.user.id, name):
                embed = discord.Embed(
                    title="📋 Playlist Created",
                    description=f"Playlist '{name}' has been created!",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"❌ Playlist '{name}' already exists!")
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="playlist_add", description="Add a song to a playlist")
    @app_commands.describe(
        playlist="Playlist name",
        query="Song name or YouTube URL"
    )
    async def add_to_playlist(self, interaction: discord.Interaction, playlist: str, query: str):
        """Add a song to a playlist"""
        await interaction.response.defer()
        
        try:
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
            
            if self.playlist_manager.add_to_playlist(interaction.user.id, playlist, track_info):
                embed = discord.Embed(
                    title="✅ Added to Playlist",
                    description=f"**{track_info['title']}** has been added to '{playlist}'",
                    color=discord.Color.green()
                )
                if track_info['thumbnail']:
                    embed.set_thumbnail(url=track_info['thumbnail'])
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"❌ Playlist '{playlist}' not found!")
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="playlist_list", description="List all your playlists")
    async def list_playlists(self, interaction: discord.Interaction):
        """List all playlists for the user"""
        await interaction.response.defer()
        
        try:
            playlists = self.playlist_manager.list_playlists(interaction.user.id)
            
            if not playlists:
                await interaction.followup.send("❌ You don't have any playlists yet!")
                return
            
            embed = discord.Embed(
                title="📋 Your Playlists",
                color=discord.Color.blurple()
            )
            
            for playlist in playlists:
                playlist_tracks = self.playlist_manager.get_playlist(interaction.user.id, playlist)
                embed.add_field(
                    name=playlist,
                    value=f"{len(playlist_tracks)} songs",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="playlist_view", description="View songs in a playlist")
    @app_commands.describe(name="Playlist name")
    async def view_playlist(self, interaction: discord.Interaction, name: str):
        """View all songs in a playlist"""
        await interaction.response.defer()
        
        try:
            tracks = self.playlist_manager.get_playlist(interaction.user.id, name)
            
            if not tracks:
                await interaction.followup.send(f"❌ Playlist '{name}' is empty or doesn't exist!")
                return
            
            embed = discord.Embed(
                title=f"📋 {name}",
                color=discord.Color.blurple()
            )
            
            for i, track in enumerate(tracks[:10], 1):
                embed.add_field(
                    name=f"{i}. {track['title']}",
                    value=f"Duration: {track['duration']}s",
                    inline=False
                )
            
            if len(tracks) > 10:
                embed.add_field(
                    name="...",
                    value=f"And {len(tracks) - 10} more songs",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="playlist_delete", description="Delete a playlist")
    @app_commands.describe(name="Playlist name")
    async def delete_playlist(self, interaction: discord.Interaction, name: str):
        """Delete a playlist"""
        await interaction.response.defer()
        
        try:
            if self.playlist_manager.delete_playlist(interaction.user.id, name):
                embed = discord.Embed(
                    title="🗑️ Playlist Deleted",
                    description=f"Playlist '{name}' has been deleted!",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send(f"❌ Playlist '{name}' not found!")
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="playlist_play", description="Play an entire playlist")
    @app_commands.describe(name="Playlist name")
    async def play_playlist(self, interaction: discord.Interaction, name: str):
        """Play an entire playlist"""
        await interaction.response.defer()
        
        try:
            # Check if user is in a voice channel
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send("❌ You must be in a voice channel!")
                return
            
            tracks = self.playlist_manager.get_playlist(interaction.user.id, name)
            
            if not tracks:
                await interaction.followup.send(f"❌ Playlist '{name}' is empty or doesn't exist!")
                return
            
            # Connect to voice if not already connected
            voice_channel = interaction.user.voice.channel
            guild_id = interaction.guild.id
            
            if not interaction.guild.voice_client:
                try:
                    await voice_channel.connect()
                except Exception as e:
                    await interaction.followup.send(f"❌ Could not connect to voice: {e}")
                    return
            
            # Import MusicManager here to add tracks to queue
            from utils.music_manager import MusicManager
            music_manager = MusicManager()
            
            for track in tracks:
                music_manager.add_to_queue(guild_id, track)
            
            embed = discord.Embed(
                title="🎵 Playlist Added to Queue",
                description=f"**{name}** with {len(tracks)} songs added to queue!",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(PlaylistCommands(bot))
