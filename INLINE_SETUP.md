# Inline Bot Setup Guide

## Enable Inline Mode for Your Bot

To use your bot inline (type `@your_bot_username` in any chat), you need to enable inline mode:

### Step 1: Enable Inline Mode
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Send `/setinline`
3. Select your bot from the list
4. Send a placeholder text (e.g., "Send stored video")
5. BotFather will confirm inline mode is enabled

### Step 2: How to Use

#### Store a Video:
1. Send a video to your bot
2. Bot will confirm: "✅ Video stored successfully!"

#### Send Video in Any Chat:
1. In any chat (private, group, channel), type: `@your_bot_username`
2. You'll see "Send stored video" option
3. Click it to send the video in that chat

### Step 3: Alternative Commands
- `/sendTheVideo <user_id>` - Send to specific user (requires user to have started bot)
- `/clearVideo` - Clear stored video
- `/videoStatus` - Check if video is stored

## Benefits of Inline Mode
- ✅ Works in any chat without leaving
- ✅ No need to add bot to groups
- ✅ User-friendly interface
- ✅ Works in private chats between you and someone else

## Example Usage
1. Send video to bot: `@your_bot_username`
2. In private chat with friend: Type `@your_bot_username`
3. Click "Send stored video"
4. Video appears in your chat with friend!
