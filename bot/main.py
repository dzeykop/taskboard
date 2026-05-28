import os
import logging
from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, ConversationHandler, MessageHandler, CallbackQueryHandler, filters

load_dotenv('/opt/taskboard/.env')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

from handlers import (start, aufgabe_start, aufgabe_text, aufgabe_name,
                      reparatur_start, reparatur_text, reparatur_name,
                      erledigt_start, erledigt_wahl,
                      nichterledigt_start, nichterledigt_wahl,
                      abbrechen, aufgaben_liste,
                      AUFGABE_TEXT, AUFGABE_NAME,
                      REPARATUR_TEXT, REPARATUR_NAME,
                      ERLEDIGT_WAHL, NICHTERLEDIGT_WAHL)

def main():
    token = os.getenv('TELEGRAM_TOKEN')
    if not token:
        print("FEHLER: TELEGRAM_TOKEN nicht gefunden in .env!")
        return

    app = Application.builder().token(token).build()

    aufgabe_conv = ConversationHandler(
        entry_points=[CommandHandler("aufgabe", aufgabe_start)],
        states={
            AUFGABE_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, aufgabe_text)],
            AUFGABE_NAME: [CallbackQueryHandler(aufgabe_name, pattern="^name_")],
        },
        fallbacks=[CommandHandler("abbrechen", abbrechen)]
    )

    reparatur_conv = ConversationHandler(
        entry_points=[CommandHandler("reparatur", reparatur_start)],
        states={
            REPARATUR_TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, reparatur_text)],
            REPARATUR_NAME: [CallbackQueryHandler(reparatur_name, pattern="^name_")],
        },
        fallbacks=[CommandHandler("abbrechen", abbrechen)]
    )

    erledigt_conv = ConversationHandler(
        entry_points=[CommandHandler("erledigt", erledigt_start)],
        states={
            ERLEDIGT_WAHL: [CallbackQueryHandler(erledigt_wahl, pattern="^erl_")],
        },
        fallbacks=[CommandHandler("abbrechen", abbrechen)]
    )

    nichterledigt_conv = ConversationHandler(
        entry_points=[CommandHandler("nichterledigt", nichterledigt_start)],
        states={
            NICHTERLEDIGT_WAHL: [CallbackQueryHandler(nichterledigt_wahl, pattern="^nierl_")],
        },
        fallbacks=[CommandHandler("abbrechen", abbrechen)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(aufgabe_conv)
    app.add_handler(reparatur_conv)
    app.add_handler(erledigt_conv)
    app.add_handler(nichterledigt_conv)
    app.add_handler(CommandHandler("aufgaben", aufgaben_liste))

    print("Bot läuft...")
    app.run_polling()

if __name__ == '__main__':
    main()
