# Telegram Homelab Monitor

A small Telegram bot to monitor a self-hosted Docker server: on-demand system
vitals (CPU, RAM, disk, temperature), plus automatic alerts when a container
goes down or comes back online.

## Features

- `/start` — welcome message
- `/status` — real-time CPU, RAM, disk and CPU temperature
- Automatic **DOWN / UP** alerts for a list of Docker containers

## Installation

```bash
git clone https://github.com/Zlsxa/tlg_bot_server_info.git
cd tlg_bot_server_info

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

All configuration is handled through a `.env` file (never committed).

```bash
cp .env.example .env
# then edit .env with your own values
```

| Variable | Description |
|---|---|
| `TELEGRAM_TOKEN` | Token issued by [@BotFather](https://t.me/BotFather) |
| `CHAT_ID_ALERTE` | Your chat ID, obtained via [@userinfobot](https://t.me/userinfobot) |
| `SERVER_NAME` | Name shown in messages (free text) |
| `CONTENEURS_A_SURVEILLER` | Containers to monitor, comma-separated |
| `INTERVALLE_CHECK` | Check interval in seconds (default: 60) |

## Running

```bash
python bot.py
```

The bot needs access to the Docker socket (`docker.from_env()`), so run it on
the machine that hosts the containers, using a user that belongs to the
`docker` group.

## Security

- Never put your token or chat ID directly in the code — everything lives in `.env`.
- `.env` is ignored by git (see `.gitignore`). Run `git status` and confirm it
  does not appear before pushing.
- If a token is ever exposed (screenshot, commit, etc.), revoke it immediately
  via @BotFather and generate a new one.

## License

MIT (or any license of your choice).
