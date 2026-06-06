# 🎵 Advanced Discord Music Bot

A feature-rich Discord music bot with personal voice channels, private playlists, and advanced music controls.

## Features

✨ **Music Streaming** - Play music directly from YouTube
✨ **Personal Voice Channels** - Create private voice channels with control panels
✨ **Private Playlists** - Create and manage your own playlists (only you can see them)
✨ **Advanced Queue System** - Full queue management and song ordering
✨ **Music Controls** - Play, pause, resume, skip, stop commands
✨ **Real-time Info** - See current song info, queue status, and more

## Commands

### 🎵 Music Commands
- `/play` - Play a song from YouTube
- `/pause` - Pause the current song
- `/resume` - Resume the song
- `/skip` - Skip to the next song
- `/stop` - Stop music and disconnect from voice
- `/queue` - View the current song queue

### 📋 Playlist Commands
- `/playlist_create` - Create a new private playlist
- `/playlist_add` - Add a song to your playlist
- `/playlist_list` - List all your playlists
- `/playlist_view` - View songs in a playlist
- `/playlist_delete` - Delete a playlist
- `/playlist_play` - Play an entire playlist

### 🎙️ Voice Channel Commands
- `/joinvc` - Create a personal voice channel with control panel
- `/leavevc` - Delete your personal voice channel

### ℹ️ Utility Commands
- `/help` - Show all available commands
- `/ping` - Check bot latency
- `/about` - About the bot

## Installation

### Prerequisites
- Python 3.8 or higher
- Discord Bot Token
- FFmpeg installed on your system

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/Bobdooocool/discord-music-bot.git
cd discord-music-bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables**
```bash
cp .env.example .env
```

4. **Add your Discord token to `.env`**
```
DISCORD_TOKEN=your_bot_token_here
```

5. **Run the bot**
```bash
python bot.py
```

## Getting Your Bot Token

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the token and paste it in `.env`
5. Enable these intents under "Privileged Gateway Intents":
   - Message Content Intent
   - Guild Members Intent
   - Voice States Intent

## Inviting the Bot to Your Server

1. Go to OAuth2 > URL Generator in Developer Portal
2. Select scopes: `bot`
3. Select permissions:
   - Manage Channels
   - Connect
   - Speak
   - Read Messages/View Channels
   - Send Messages
   - Embed Links
4. Copy the generated URL and open it in your browser

## Deployment

### Replit
1. Import this repository to Replit
2. Add `DISCORD_TOKEN` as a secret
3. Run the bot
4. (Optional) Use Replit's "Always On" feature to keep it running 24/7

### Other Hosting
- Railway
- Render
- Heroku
- Your own server/VPS

## Advanced Features

### Personal Voice Channels
- Use `/joinvc` to create a personal voice channel
- Only you can see and access your channel
- Get a private control panel with all music commands
- Channel automatically deletes when you leave

### Private Playlists
- Create multiple playlists with `/playlist_create`
- Add any YouTube song with `/playlist_add`
- Playlists are 100% private - only you can see them
- Play entire playlists with `/playlist_play`

### Smart Queue Management
- Automatic queue progression
- View upcoming songs with `/queue`
- Easy song skipping and management

## Troubleshooting

### Bot won't start
- Make sure you have a valid Discord token in `.env`
- Check that all dependencies are installed: `pip install -r requirements.txt`

### No audio
- Make sure FFmpeg is installed on your system
- Check that the bot has voice permissions on your server

### Commands not showing up
- The bot needs to sync commands with Discord (automatic on startup)
- Try restarting the bot if commands take a while to appear

### Connection issues
- Make sure the bot is in the voice channel
- Check your internet connection
- Try reconnecting with `/stop` then `/play`

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on GitHub or contact the developer.

---

Made with ❤️ for the Discord community
