## nihuyaNeUnderstandBot (inline video bot)

### Features
- Owner uploads a video via direct chat; bot stores its `file_id` in SQLite.
- `/status` tells whether a video is stored.
- Inline query returns the stored video using a cached file id.

### Requirements
- Python 3.8 (server has 3.8.10). Local dev should use Python 3.8 to match.

### Setup (local)
1. Create and activate a Python 3.8 virtualenv
2. `pip install -r requirements.txt`
3. Set env vars:
   - `BOT_TOKEN` – bot token
   - `BOT_OWNER_ID` – owner Telegram numeric user id
   - optional: `BOT_DB_PATH` – default `./data/bot.db`
4. Run:
```bash
python -m bot.main
```

### Build PEX (single-file)
```bash
./scripts/build_pex.sh
```
Outputs `dist/bot.pex` which can run on Ubuntu 20.04 x86_64 with Python 3.8.

### Server deployment (root-only safe)
1. Copy `dist/bot.pex` and `.env` (or set env on cron wrapper if desired) to e.g. `/opt/nihuya-bot/`
2. Create `/opt/nihuya-bot/scripts/start.sh` (already in repo) and adjust paths if needed
3. Add to root's crontab (pick user):
```bash
@reboot /usr/sbin/runuser -u nobody -- /opt/nihuya-bot/scripts/start.sh
```
4. Logs: `/opt/nihuya-bot/bot.log`

### Notes
- Avoid native/compiled dependencies to ensure cross-platform build.
- Inline results are cached briefly (2s) to reduce stale responses.


