import discord
from discord.ext import commands
from discord import app_commands

class UtilityCommands(commands.Cog):
    """Utility and info commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        """Show help information"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🎵 Music Bot Help",
                description="Advanced Discord Music Bot",
                color=discord.Color.blurple()
            )
            
            # Music Commands
            embed.add_field(
                name="🎵 Music Commands",
                value="""
/play - Play a song from YouTube
/pause - Pause the current song
/resume - Resume the song
/skip - Skip to next song
/stop - Stop music and disconnect
/queue - View the current queue
                """,
                inline=False
            )
            
            # Playlist Commands
            embed.add_field(
                name="📋 Playlist Commands",
                value="""
/playlist_create - Create a new playlist
/playlist_add - Add a song to a playlist
/playlist_list - List all your playlists
/playlist_view - View songs in a playlist
/playlist_delete - Delete a playlist
/playlist_play - Play an entire playlist
                """,
                inline=False
            )
            
            # VC Commands
            embed.add_field(
                name="🎙️ Voice Channel Commands",
                value="""
/joinvc - Create a personal voice channel
/leavevc - Delete your personal voice channel
                """,
                inline=False
            )
            
            # Utility
            embed.add_field(
                name="ℹ️ Utility Commands",
                value="""
/help - Show this help message
/ping - Check bot latency
/about - About this bot
                """,
                inline=False
            )
            
            embed.set_footer(text="All playlists are private and only visible to you!")
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot ping"""
        await interaction.response.defer()
        
        try:
            latency = self.bot.latency * 1000
            embed = discord.Embed(
                title="🏓 Pong!",
                description=f"Latency: **{latency:.2f}ms**",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="about", description="About this bot")
    async def about(self, interaction: discord.Interaction):
        """About the bot"""
        await interaction.response.defer()
        
        try:
            embed = discord.Embed(
                title="🎵 About This Bot",
                description="Advanced Discord Music Bot",
                color=discord.Color.blurple()
            )
            
            embed.add_field(
                name="Features",
                value="""
✨ YouTube Music Streaming
✨ Personal Voice Channels
✨ Private Playlists
✨ Advanced Queue System
✨ Full Music Controls
                """,
                inline=False
            )
            
            embed.add_field(
                name="Version",
                value="1.0.0",
                inline=True
            )
            
            embed.add_field(
                name="Status",
                value="🟢 Online",
                inline=True
            )
            
            embed.set_footer(text="Built with discord.py | Python")
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

async def setup(bot):
    await bot.add_cog(UtilityCommands(bot))
