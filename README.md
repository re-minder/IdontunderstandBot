# Video Sending Bot

A simple Telegram bot that stores a video and allows you to send it in any chat using inline mode.

## Features

- Store one video at a time
- Send the stored video in any chat using `@your_bot_username`
- Works in private chats, groups, and channels
- No need to leave your current conversation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your bot token:
   - Create a bot with [@BotFather](https://t.me/botfather) on Telegram
   - Copy the bot token
   - Create a `.env` file and add: `BOT_TOKEN=your_bot_token_here`

3. Enable inline mode:
   - Message [@BotFather](https://t.me/botfather)
   - Send `/setinline`
   - Select your bot
   - Set placeholder text: "Send stored video"

4. Run the bot:
```bash
python bot.py
```

## Usage

1. **Store a video**: Send a video to your bot
2. **Send in any chat**: Type `@your_bot_username` in any chat and click "Send stored video"

## Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/clearVideo` - Clear stored video
- `/videoStatus` - Check if video is stored

## Project Structure

- `bot.py` - Main bot file
- `config.py` - Configuration settings
- `handlers/` - Command and video handlers
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create this file)
- `.gitignore` - Git ignore file
