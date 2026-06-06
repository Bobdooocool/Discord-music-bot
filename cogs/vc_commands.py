import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from utils.voice_manager import VoiceManager

class VCCommands(commands.Cog):
    """Advanced voice channel management with join-to-create"""
    
    def __init__(self, bot):
        self.bot = bot
        self.voice_manager = VoiceManager()
        self.jtc_category: dict = {}  # guild_id -> category_id (join-to-create)
        self.vc_panels: dict = {}  # channel_id -> control_panel_message_id
    
    @app_commands.command(name="setup_jtc", description="Setup Join-to-Create voice channel")
    async def setup_jtc(self, interaction: discord.Interaction):
        """Setup a join-to-create voice channel"""
        await interaction.response.defer()
        
        try:
            guild = interaction.guild
            
            # Create category for personal VCs
            category = await guild.create_category("🎵 Personal VCs")
            
            # Create the join-to-create channel
            jtc_channel = await category.create_voice_channel(
                "➕ Create Personal VC",
                user_limit=1
            )
            
            self.jtc_category[guild.id] = category.id
            
            embed = discord.Embed(
                title="✅ Join-to-Create Setup",
                description=f"Created: {jtc_channel.mention}",
                color=discord.Color.green()
            )
            embed.add_field(
                name="How it works",
                value="Join the **➕ Create Personal VC** channel and a private voice channel will be created for you!",
                inline=False
            )
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
            print(f"Setup JTC error: {e}")
    
    @app_commands.command(name="vc_lock", description="Lock your personal voice channel")
    async def vc_lock(self, interaction: discord.Interaction):
        """Lock your personal voice channel"""
        await interaction.response.defer()
        
        try:
            # Get user's voice channel
            if not interaction.user.voice or not interaction.user.voice.channel:
                embed = discord.Embed(title="❌ Not in Voice", description="You must be in a voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            channel = interaction.user.voice.channel
            
            # Check if it's their personal channel
            owner_id = self.voice_manager.get_channel_owner(channel.id)
            if owner_id != interaction.user.id:
                embed = discord.Embed(title="❌ Not Your Channel", description="This is not your personal voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            # Lock the channel
            await channel.edit(user_limit=len(channel.members))
            
            embed = discord.Embed(
                title="🔒 Channel Locked",
                description=f"Channel is now locked with {len(channel.members)} members",
                color=discord.Color.yellow()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="vc_unlock", description="Unlock your personal voice channel")
    async def vc_unlock(self, interaction: discord.Interaction):
        """Unlock your personal voice channel"""
        await interaction.response.defer()
        
        try:
            if not interaction.user.voice or not interaction.user.voice.channel:
                embed = discord.Embed(title="❌ Not in Voice", description="You must be in a voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            channel = interaction.user.voice.channel
            owner_id = self.voice_manager.get_channel_owner(channel.id)
            
            if owner_id != interaction.user.id:
                embed = discord.Embed(title="❌ Not Your Channel", description="This is not your personal voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            # Unlock the channel
            await channel.edit(user_limit=None)
            
            embed = discord.Embed(
                title="🔓 Channel Unlocked",
                description="Channel is now open for anyone to join",
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="vc_limit", description="Set user limit for your voice channel")
    @app_commands.describe(limit="User limit (0 for unlimited)")
    async def vc_limit(self, interaction: discord.Interaction, limit: int):
        """Set user limit"""
        await interaction.response.defer()
        
        try:
            if not interaction.user.voice or not interaction.user.voice.channel:
                embed = discord.Embed(title="❌ Not in Voice", description="You must be in a voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            channel = interaction.user.voice.channel
            owner_id = self.voice_manager.get_channel_owner(channel.id)
            
            if owner_id != interaction.user.id:
                embed = discord.Embed(title="❌ Not Your Channel", description="This is not your personal voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            if limit < 0 or limit > 99:
                embed = discord.Embed(title="❌ Invalid Limit", description="Limit must be between 0-99!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            await channel.edit(user_limit=limit if limit > 0 else None)
            
            limit_text = "Unlimited" if limit == 0 else f"{limit} users"
            embed = discord.Embed(
                title="👥 User Limit Updated",
                description=f"Channel limit is now: **{limit_text}**",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="vc_kick", description="Kick a user from your voice channel")
    @app_commands.describe(user="User to kick")
    async def vc_kick(self, interaction: discord.Interaction, user: discord.User):
        """Kick a user from your channel"""
        await interaction.response.defer()
        
        try:
            if not interaction.user.voice or not interaction.user.voice.channel:
                embed = discord.Embed(title="❌ Not in Voice", description="You must be in a voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            channel = interaction.user.voice.channel
            owner_id = self.voice_manager.get_channel_owner(channel.id)
            
            if owner_id != interaction.user.id:
                embed = discord.Embed(title="❌ Not Your Channel", description="This is not your personal voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            member = interaction.guild.get_member(user.id)
            if not member or not member.voice or member.voice.channel.id != channel.id:
                embed = discord.Embed(title="❌ Not in Channel", description="That user is not in your channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            await member.move_to(None)
            
            embed = discord.Embed(
                title="👋 User Kicked",
                description=f"**{user.name}** has been removed from your channel",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="vc_info", description="View your voice channel info")
    async def vc_info(self, interaction: discord.Interaction):
        """Show VC info"""
        await interaction.response.defer()
        
        try:
            if not interaction.user.voice or not interaction.user.voice.channel:
                embed = discord.Embed(title="❌ Not in Voice", description="You must be in a voice channel!", color=discord.Color.red())
                await interaction.followup.send(embed=embed)
                return
            
            channel = interaction.user.voice.channel
            
            embed = discord.Embed(
                title="🎙️ Voice Channel Info",
                color=discord.Color.blurple()
            )
            embed.add_field(name="Channel", value=channel.mention, inline=False)
            embed.add_field(name="Members", value=f"{len(channel.members)}", inline=True)
            embed.add_field(name="Limit", value=f"{channel.user_limit if channel.user_limit else 'Unlimited'}", inline=True)
            embed.add_field(name="Bitrate", value=f"{channel.bitrate // 1000}kbps", inline=True)
            
            await interaction.followup.send(embed=embed)
        
        except Exception as e:
            embed = discord.Embed(title="❌ Error", description=str(e), color=discord.Color.red())
            await interaction.followup.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handle voice state changes for join-to-create"""
        try:
            # User joined a channel
            if not before.channel and after.channel:
                channel = after.channel
                guild = member.guild
                
                # Check if it's a join-to-create channel
                jtc_category_id = self.jtc_category.get(guild.id)
                
                if channel.name == "➕ Create Personal VC" and channel.category_id == jtc_category_id:
                    # Create personal VC for this user
                    category = guild.get_channel(jtc_category_id)
                    
                    # Create the personal channel
                    personal_vc = await category.create_voice_channel(
                        f"🎵 {member.name}'s VC",
                        user_limit=None
                    )
                    
                    # Set permissions
                    await personal_vc.set_permissions(
                        guild.default_role,
                        connect=False,
                        speak=False,
                        view_channel=False
                    )
                    await personal_vc.set_permissions(
                        member,
                        connect=True,
                        speak=True,
                        view_channel=True,
                        manage_channels=True
                    )
                    
                    # Register the channel
                    self.voice_manager.personal_channels[member.id] = personal_vc.id
                    self.voice_manager.channel_owners[personal_vc.id] = member.id
                    
                    # Move user to personal channel
                    await member.move_to(personal_vc)
            
            # User left a channel
            elif before.channel and not after.channel:
                channel = before.channel
                owner_id = self.voice_manager.get_channel_owner(channel.id)
                
                # If personal VC and empty, delete it
                if owner_id and len(channel.members) == 0:
                    try:
                        await channel.delete()
                        self.voice_manager.personal_channels.pop(owner_id, None)
                        self.voice_manager.channel_owners.pop(channel.id, None)
                    except:
                        pass
        
        except Exception as e:
            print(f"Voice state update error: {e}")

async def setup(bot):
    await bot.add_cog(VCCommands(bot))
