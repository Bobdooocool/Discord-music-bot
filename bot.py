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

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    print(f"✅ Bot is online as {bot.user}")
    print(f"✅ Discord.py version: {discord.__version__}")
    
    # Sync commands with Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    print(f"❌ Error: {error}")

async def load_cogs():
    """Load all cogs from the cogs directory"""
    cogs_dir = "cogs"
    
    if not os.path.exists(cogs_dir):
        os.makedirs(cogs_dir)
    
    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            cog_name = filename[:-3]
            try:
                await bot.load_extension(f"cogs.{cog_name}")
                print(f"✅ Loaded cog: {cog_name}")
            except Exception as e:
                print(f"❌ Failed to load cog {cog_name}: {e}")

async def main():
    """Main function to start the bot"""
    async with bot:
        # Load cogs
        await load_cogs()
        
        # Get token from environment
        token = os.getenv("DISCORD_TOKEN")
        
        if not token:
            print("❌ ERROR: DISCORD_TOKEN not found in .env file!")
            print("Please add your bot token to the .env file")
            return
        
        try:
            await bot.start(token)
        except discord.LoginFailure:
            print("❌ Invalid token! Please check your DISCORD_TOKEN")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
