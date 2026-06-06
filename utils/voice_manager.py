import discord
from typing import Dict, Optional

class VoiceManager:
    """Manages voice channel creation and management"""
    
    def __init__(self):
        self.personal_channels: Dict[int, int] = {}  # user_id -> channel_id
        self.channel_owners: Dict[int, int] = {}  # channel_id -> user_id
    
    async def create_personal_vc(self, user: discord.Member, guild: discord.Guild, category: discord.CategoryChannel = None) -> Optional[discord.VoiceChannel]:
        """Create a personal voice channel for a user"""
        try:
            # Create channel with restricted permissions
            permissions = {
                guild.default_role: discord.PermissionOverwrite(
                    connect=False,
                    speak=False,
                    view_channel=False
                ),
                user: discord.PermissionOverwrite(
                    connect=True,
                    speak=True,
                    view_channel=True,
                    manage_channels=True
                )
            }
            
            channel = await guild.create_voice_channel(
                f"🎵 {user.name}'s Music",
                category=category,
                overwrites=permissions
            )
            
            self.personal_channels[user.id] = channel.id
            self.channel_owners[channel.id] = user.id
            
            return channel
        except Exception as e:
            print(f"Error creating personal VC: {e}")
            return None
    
    async def delete_personal_vc(self, user_id: int):
        """Delete a personal voice channel"""
        try:
            if user_id in self.personal_channels:
                channel_id = self.personal_channels[user_id]
                # Channel will be deleted when empty or manually
                del self.personal_channels[user_id]
                if channel_id in self.channel_owners:
                    del self.channel_owners[channel_id]
        except Exception as e:
            print(f"Error deleting personal VC: {e}")
    
    def get_personal_channel(self, user_id: int) -> Optional[int]:
        """Get user's personal channel ID"""
        return self.personal_channels.get(user_id)
    
    def get_channel_owner(self, channel_id: int) -> Optional[int]:
        """Get the owner of a channel"""
        return self.channel_owners.get(channel_id)
