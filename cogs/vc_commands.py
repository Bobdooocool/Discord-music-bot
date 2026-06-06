import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.voice_manager import VoiceManager

class VCCommands(commands.Cog):
    """Voice channel management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_manager = VoiceManager()
        self.control_panels = {}  # guild_id -> message_id
    
    @app_commands.command(name="joinvc", description="Create a personal voice channel")
    async def join_vc(self, interaction: discord.Interaction):
        """Create a personal voice channel for the user"""
        await interaction.response.defer()
        
        try:
            # Check if user is in a voice channel
            if not interaction.user.voice or not interaction.user.voice.channel:
                await interaction.followup.send("❌ You must be in a voice channel first!")
                return
            
            guild = interaction.guild
            user = interaction.user
            
            # Check if user already has a personal channel
            if self.voice_manager.get_personal_channel(user.id):
                await interaction.followup.send("❌ You already have a personal voice channel!")
                return
            
            # Create the personal voice channel
            embed = discord.Embed(
                title="🎵 Creating Personal VC...",
                description="Setting up your personal voice channel...",
                color=discord.Color.blurple()
            )
            await interaction.followup.send(embed=embed)
            
            personal_channel = await self.voice_manager.create_personal_vc(user, guild)
            
            if not personal_channel:
                await interaction.followup.send("❌ Failed to create personal voice channel!")
                return
            
            # Move user to the new channel
            await user.move_to(personal_channel)
            
            # Create control panel
            panel_embed = discord.Embed(
                title="🎛️ Music Control Panel",
                description=f"Personal VC for {user.name}",
                color=discord.Color.blurple()
            )
            panel_embed.add_field(name="Commands", value="/play - Play a song\n/pause - Pause\n/resume - Resume\n/skip - Skip\n/queue - View queue\n/stop - Stop", inline=False)
            panel_embed.set_footer(text="This panel is only visible to you")
            
            # Send control panel as ephemeral message
            await user.send(embed=panel_embed)
            
            success_embed = discord.Embed(
                title="✅ Personal VC Created",
                description=f"Your personal voice channel **{personal_channel.name}** has been created!",
                color=discord.Color.green()
            )
            success_embed.add_field(name="Channel", value=personal_channel.mention, inline=False)
            
            await interaction.followup.send(embed=success_embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @app_commands.command(name="leavevc", description="Leave and delete your personal voice channel")
    async def leave_vc(self, interaction: discord.Interaction):
        """Leave and delete the personal voice channel"""
        await interaction.response.defer()
        
        try:
            user_id = interaction.user.id
            channel_id = self.voice_manager.get_personal_channel(user_id)
            
            if not channel_id:
                await interaction.followup.send("❌ You don't have a personal voice channel!")
                return
            
            channel = interaction.guild.get_channel(channel_id)
            
            if channel:
                # Move user out if they're in the channel
                if interaction.user.voice and interaction.user.voice.channel.id == channel_id:
                    await interaction.user.move_to(None)
                
                await channel.delete()
            
            await self.voice_manager.delete_personal_vc(user_id)
            
            embed = discord.Embed(
                title="✅ VC Deleted",
                description="Your personal voice channel has been deleted!",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state changes"""
        try:
            # If user left a voice channel
            if before.channel and not after.channel:
                channel_id = before.channel.id
                owner_id = self.voice_manager.get_channel_owner(channel_id)
                
                # If this is a personal VC and it's empty, delete it
                if owner_id and before.channel.members:
                    return
                
                if owner_id and not before.channel.members:
                    try:
                        await before.channel.delete()
                        await self.voice_manager.delete_personal_vc(owner_id)
                    except:
                        pass
        
        except Exception as e:
            print(f"Error in voice state update: {e}")

async def setup(bot):
    await bot.add_cog(VCCommands(bot))
