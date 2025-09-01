# Video Sending Bot

A simple Telegram bot that stores a video and allows you to send it in any chat using inline mode.

## Features

- Store one video at a time
- Send the stored video in any chat using `@nihuyaNeUnderstandBot`
- Works in private chats, groups, and channels
- No need to leave your current conversation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The `.env` file is already configured with your bot token.

3. Run the bot:
```bash
python bot.py
```

## Usage

1. **Store a video**: Send a video to your bot
2. **Send in any chat**: Type `@nihuyaNeUnderstandBot` in any chat and click "Send stored video"

## Commands

- `/start` - Start the bot
- `/status` - Check if video is stored
- `/clear` - Clear stored video

## How it works

1. Send a video to the bot → It gets stored
2. In any chat, type `@nihuyaNeUnderstandBot` → See "Send stored video" option
3. Click it → Video appears in that chat!
