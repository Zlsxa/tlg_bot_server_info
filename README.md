# Telegram Homelab Monitor

Petit bot Telegram pour surveiller un serveur Docker maison :
constantes système (CPU, RAM, disque, température) à la demande, et
alertes automatiques quand un conteneur tombe ou revient en ligne.

## Fonctionnalités

- `/start` : message de bienvenue
- `/status` : CPU, RAM, disque et température CPU en temps réel
- Alertes automatiques **DOWN / UP** sur une liste de conteneurs Docker

## Installation

```bash
git clone <ton-repo>
cd telegram-homelab-bot

python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

Toute la configuration passe par un fichier `.env` (jamais commité).

```bash
cp .env.example .env
# puis édite .env avec tes valeurs
```

| Variable | Description |
|---|---|
| `TELEGRAM_TOKEN` | Token donné par [@BotFather](https://t.me/BotFather) |
| `CHAT_ID_ALERTE` | Ton ID de chat, obtenu via [@userinfobot](https://t.me/userinfobot) |
| `SERVER_NAME` | Nom affiché dans les messages (libre) |
| `CONTENEURS_A_SURVEILLER` | Conteneurs à surveiller, séparés par des virgules |
| `INTERVALLE_CHECK` | Intervalle de vérification en secondes (défaut : 60) |

## Lancement

```bash
python bot.py
```

Le bot a besoin d'un accès au socket Docker (`docker.from_env()`),
donc lance-le sur la machine qui héberge les conteneurs, avec un
utilisateur membre du groupe `docker`.

## Sécurité

- Ne mets **jamais** ton token ou ton chat ID dans le code : tout est dans `.env`.
- `.env` est ignoré par git (voir `.gitignore`). Vérifie avec `git status`
  qu'il n'apparaît pas avant de pousser.
- Si un token a déjà fuité (capture d'écran, commit, etc.), révoque-le
  immédiatement via @BotFather et régénères-en un nouveau.

## Licence

À toi de choisir (MIT par ex.).
