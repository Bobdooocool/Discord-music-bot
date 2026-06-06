import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.guild_messages = True
intents.direct_messages = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f"\n{'='*50}")
    print(f"✅ Bot is online as {bot.user}")
    print(f"✅ Discord.py version: {discord.__version__}")
    print(f"✅ Loaded cogs: {len(bot.cogs)}")
    print(f"{'='*50}\n")
    
    # Sync commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash command(s) with Discord!")
        for cmd in synced:
            print(f"  - /{cmd.name}")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    print(f"❌ Command Error: {error}")

async def load_cogs():
    """Load all cogs from the cogs directory"""
    cogs_dir = "cogs"
    
    if not os.path.exists(cogs_dir):
        print(f"❌ Cogs directory not found: {cogs_dir}")
        os.makedirs(cogs_dir)
        return
    
    cog_count = 0
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"✅ Loaded cog: {cog_name}")
                cog_count += 1
            except Exception as e:
                print(f"❌ Failed to load cog {cog_name}: {e}")
    
    print(f"\n✅ Total cogs loaded: {cog_count}\n")

async def main():
    """Main function to start the bot"""
    async with bot:
        # Load cogs first
        print("Loading cogs...\n")
        await load_cogs()
        
        # Get token from environment
        token = os.getenv("DISCORD_TOKEN")
        
        if not token:
            print("❌ ERROR: DISCORD_TOKEN not found!")
            print("Please add your bot token as a Secret in Replit:")
            print("  Key: DISCORD_TOKEN")
            print("  Value: your_bot_token_here")
            return
        
        try:
            print("🚀 Starting bot...\n")
            await bot.start(token)
        except discord.LoginFailure:
            print("❌ Invalid token! Please check your DISCORD_TOKEN")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
