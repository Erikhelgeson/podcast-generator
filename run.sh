#!/bin/bash

# 1. Credentials for background launchd execution
source ~/Developer/podcast-generator/.env
export GMAIL_USER=erikrhelgeson@gmail.com
export GMAIL_PASS=35Jumbos!

# Wait 10 seconds for Wi-Fi reconnection if woken from sleep
sleep 10

# 2. 3-Day Cleanup: Delete MP3s and prompt scripts older than 3 days
PODCAST_OUT="$HOME/Documents/Personal/Daily podcasts"
[ ! -d "$PODCAST_OUT" ] && PODCAST_OUT="$HOME/Documents/personal/Daily podcasts"

if [ -d "$PODCAST_OUT" ]; then
    find "$PODCAST_OUT" -type f -name "*.mp3" -mtime +3 -delete
    find "$PODCAST_OUT" -type f -name "podcast_script_*.txt" -mtime +3 -delete
fi

# 3. Execute generator script from project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
/usr/bin/caffeinate -u -t 600 /usr/bin/python3 "$SCRIPT_DIR/src/generate_script.py" >> "$SCRIPT_DIR/podcast.log" 2>&1