import os
import yaml
from telegram import Update
from telegram.ext import ContextTypes
from database import Aufgabe, session

def lade_mitarbeiter():
    with open('/opt/taskboard/config/mitarbeiter.yaml', 'r') as f:
        return yaml.safe_load(f)['mitarbeiter']

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hallo {user.first_name}!\n"
        f"Deine Telegram-ID: {user.id}\n\n"
        f"Befehle:\n"
        f"/aufgabe [Text] [@name] - Neue Aufgabe\n"
        f"/erledigt [ID] - Aufgabe erledigt\n"
        f"/aufgaben - Alle offenen Aufgaben"
    )

async def neue_aufgabe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Verwendung: /aufgabe Pumpe reparieren @max")
        return

    text = ' '.join(context.args)
    zugewiesen = None

    mitarbeiter = lade_mitarbeiter()
    for m in mitarbeiter:
        vorname = m['name'].split()[0].lower()
        if f"@{vorname}" in text.lower():
            zugewiesen = m['name']
            text = text.replace(f"@{vorname}", "").strip()

    aufgabe = Aufgabe(beschreibung=text, zugewiesen_an=zugewiesen)
    session.add(aufgabe)
    session.commit()

    antwort = f"✓ Aufgabe #{aufgabe.id} erstellt: {text}"
    if zugewiesen:
        antwort += f"\nZugewiesen an: {zugewiesen}"
    await update.message.reply_text(antwort)

async def erledigt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Verwendung: /erledigt 5")
        return

    try:
        aufgabe_id = int(context.args[0])
        aufgabe = session.get(Aufgabe, aufgabe_id)
        if not aufgabe:
            await update.message.reply_text(f"Aufgabe #{aufgabe_id} nicht gefunden!")
            return
        aufgabe.erledigt = True
        session.commit()
        await update.message.reply_text(f"✓ Aufgabe #{aufgabe_id} als erledigt markiert!")
    except ValueError:
        await update.message.reply_text("Bitte eine gültige Nummer angeben!")

async def aufgaben_liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    aufgaben = session.query(Aufgabe).filter_by(erledigt=False).all()
    if not aufgaben:
        await update.message.reply_text("Keine offenen Aufgaben!")
        return

    text = "📋 Offene Aufgaben:\n\n"
    for a in aufgaben:
        text += f"#{a.id} {a.beschreibung}"
        if a.zugewiesen_an:
            text += f" → {a.zugewiesen_an}"
        text += "\n"
    await update.message.reply_text(text)
