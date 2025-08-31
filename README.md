# Telegram Bot

A Telegram bot built with Python and the python-telegram-bot library.

## Features

- Basic bot functionality
- Command handling
- Message processing

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your bot token:
   - Create a bot with [@BotFather](https://t.me/botfather) on Telegram
   - Copy the bot token
   - Create a `.env` file and add: `BOT_TOKEN=your_bot_token_here`

3. Run the bot:
```bash
python bot.py
```

## Project Structure

- `bot.py` - Main bot file
- `config.py` - Configuration settings
- `handlers/` - Message and command handlers
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create this file)
- `.gitignore` - Git ignore file

## Development

This bot is built using the python-telegram-bot library and follows a modular structure for easy maintenance and extension.
