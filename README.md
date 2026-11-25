# Telegram Personal Manager (private DM assistant)

A Python + Flask + Telethon + Gemini starter. It listens to incoming **private text DMs** on your own Telegram account, generates reply drafts, and exposes a password-protected dashboard. Auto-reply is OFF by default.

## Important limitations
- This uses a Telegram **user account session** (MTProto), not a BotFather bot token.
- Render free web services can sleep and have ephemeral storage. When sleeping, the listener stops; local SQLite data may be lost on redeploy/restart. A persistent disk or always-on paid service is needed for reliable 24/7 operation.
- Do not use this for unsolicited bulk messaging, scraping, or spam. Respect Telegram rules and the privacy of people messaging you.
- DMs are sent to Google's Gemini API for reply generation. Review Google's API data-use terms before enabling this for sensitive conversations.
- Auto-reply is disabled by default. Test in approval mode first.
- This starter handles incoming private text messages only. It skips groups, bots, slash commands, and media-only messages.

## 1. Get credentials
1. Create Telegram API credentials at https://my.telegram.org (API ID and API HASH).
2. Create a Gemini API key at https://aistudio.google.com/app/apikey.
3. Install Python 3.11+ on a trusted computer. Do not generate or paste your session string into public chats.

## 2. Generate Telegram session locally
```bash
pip install -r requirements.txt
python generate_session.py
```
Complete Telegram's login/2FA prompts. Copy the printed session string directly into Render's `TG_SESSION` environment variable. Treat it like your Telegram password. Never commit it to GitHub.

## 3. Deploy to Render
1. Push these files to a **private GitHub repository**.
2. In Render, create a Web Service from that repository.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app --workers 1 --threads 4 --timeout 120`
5. Add all variables from `.env.example` in Render Environment. Use a long random `DASHBOARD_PASSWORD`.
6. Deploy. Open your service URL and sign in using `DASHBOARD_USER` and `DASHBOARD_PASSWORD`.

`render.yaml` is included as a blueprint reference. Add secrets in the Render dashboard, not in that file.

## 4. Operating modes
- Approval mode: leave `AUTO_REPLY=false`. Incoming DMs create AI drafts; open the dashboard and press **Approve & send**.
- Automatic mode: turn on Auto-reply in the dashboard. The setting is in memory and resets after a restart to the `AUTO_REPLY` environment default. Set `AUTO_REPLY=true` in Render only after testing carefully.

## 5. Customize personality
Set `AI_STYLE` in Render, for example:
`You are a friendly solo software developer. Reply in casual Hinglish, keep replies short, avoid corporate language, and ask one clear question when needed.`

## Security checklist
- Keep the GitHub repository private.
- Never commit `.env`, `TG_SESSION`, API hashes, or API keys.
- If a session string leaks, revoke active Telegram sessions from Telegram Settings > Devices and generate a new one.
- Use a strong dashboard password and HTTPS (Render provides HTTPS).
- Keep approval mode enabled until you trust the generated replies.
