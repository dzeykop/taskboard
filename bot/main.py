import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters

load_dotenv('/opt/taskboard/.env')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from handlers import start, neue_aufgabe, erledigt, aufgaben_liste

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        print("FEHLER: TELEGRAM_TOKEN nicht gefunden in .env!")
        return

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("aufgabe", neue_aufgabe))
    app.add_handler(CommandHandler("erledigt", erledigt))
    app.add_handler(CommandHandler("aufgaben", aufgaben_liste))

    print("Bot läuft...")
    app.run_polling()

if __name__ == '__main__':
    main()
