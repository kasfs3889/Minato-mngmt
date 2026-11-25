"""Run locally once to create TG_SESSION. Never share the resulting session string."""
import os
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

api_id = int(input("Telegram API ID: ").strip())
api_hash = input("Telegram API HASH: ").strip()
with TelegramClient(StringSession(), api_id, api_hash) as client:
    print("\nYour TG_SESSION (keep secret; add it only to Render environment):\n")
    print(client.session.save())
