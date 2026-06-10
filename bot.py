import os
import shutil

import psutil
import docker
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- Configuration (tout vient du fichier .env, rien en dur dans le code) ---
load_dotenv()

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID_ALERTE = int(os.environ["CHAT_ID_ALERTE"])

# Nom affiché dans les messages (par défaut générique, pas d'info sur ta machine)
SERVER_NAME = os.environ.get("SERVER_NAME", "Serveur")

# Liste de conteneurs critiques, séparés par des virgules dans le .env
CONTENEURS_A_SURVEILLER = [
    c.strip()
    for c in os.environ.get("CONTENEURS_A_SURVEILLER", "").split(",")
    if c.strip()
]

# Intervalle (en secondes) entre deux vérifications Docker
INTERVALLE_CHECK = int(os.environ.get("INTERVALLE_CHECK", "60"))

# Mémorise le dernier état connu des conteneurs (évite le spam d'alertes)
etat_precedent_conteneurs = {}


# Fonction pour interroger l'état du système
def get_system_status():
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    total, used, free = shutil.disk_usage("/")
    disk_used = (used / total) * 100

    temp_msg = "Non disponible"
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        for name in ["coretemp", "acpitz", "cpu_thermal"]:
            if name in temps and len(temps[name]) > 0:
                temp_msg = f"{temps[name][0].current}°C"
                break

    status_text = (
        f"🖥 **STATUT DU {SERVER_NAME.upper()}** 🖥\n\n"
        f"🔥 **CPU :** `{cpu}%` utilisé\n"
        f"🧠 **RAM :** `{ram}%` utilisé\n"
        f"💾 **Disque (/) :** `{disk_used:.1f}%` utilisé\n"
        f"🌡 **Température CPU :** `{temp_msg}`\n"
    )
    return status_text


# Tâche de fond : vérification des conteneurs Docker
async def alerte_docker_loop(context: ContextTypes.DEFAULT_TYPE):
    global etat_precedent_conteneurs
    try:
        client = docker.from_env()
        conteneurs = client.containers.list(all=True)

        # État actuel : { "service_a": "running", "service_b": "exited" }
        etats_actuels = {
            c.name: c.status
            for c in conteneurs
            if c.name in CONTENEURS_A_SURVEILLER
        }

        for nom_conteneur in CONTENEURS_A_SURVEILLER:
            statut_actuel = etats_actuels.get(nom_conteneur, "introuvable")
            # Par défaut on suppose que le service était sain
            statut_avant = etat_precedent_conteneurs.get(nom_conteneur, "running")

            # Le conteneur vient de tomber
            if statut_avant == "running" and statut_actuel != "running":
                message = (
                    f"🚨 **ALERTE : Le service `{nom_conteneur}` est DOWN !**\n"
                    f"Statut actuel : `{statut_actuel}`"
                )
                await context.bot.send_message(
                    chat_id=CHAT_ID_ALERTE, text=message, parse_mode="Markdown"
                )

            # Le conteneur est revenu en ligne
            elif statut_avant != "running" and statut_actuel == "running":
                message = (
                    f"✅ **RÉTABLISSEMENT : Le service `{nom_conteneur}` "
                    f"est de nouveau en ligne (UP).**"
                )
                await context.bot.send_message(
                    chat_id=CHAT_ID_ALERTE, text=message, parse_mode="Markdown"
                )

        etat_precedent_conteneurs = etats_actuels

    except Exception as e:
        print(f"Erreur lors de la vérification Docker : {e}")


# Commandes Telegram
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🛡 {SERVER_NAME} sous surveillance active.\n"
        "Tape /status pour les constantes vitales."
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_system_status(), parse_mode="Markdown")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))

    # Lance la vérification Docker en tâche de fond
    if CONTENEURS_A_SURVEILLER:
        app.job_queue.run_repeating(
            alerte_docker_loop, interval=INTERVALLE_CHECK, first=10
        )

    print(f"{SERVER_NAME} : bot démarré.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
