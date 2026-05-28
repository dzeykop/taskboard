import yaml
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database import Aufgabe, session

def lade_mitarbeiter():
    with open('/opt/taskboard/config/mitarbeiter.yaml', 'r') as f:
        return yaml.safe_load(f)['mitarbeiter']

def finde_zuweisung(text):
    mitarbeiter = lade_mitarbeiter()
    for m in mitarbeiter:
        vorname = m['name'].split()[0].lower()
        if f"@{vorname}" in text.lower():
            return m['name'], text.replace(f"@{vorname}", "").strip()
    return None, text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hallo {user.first_name}!\n"
        f"Deine Telegram-ID: {user.id}\n\n"
        f"Befehle:\n"
        f"/aufgabe [Text] [@name] - Neue Aufgabe\n"
        f"/reparatur [Text] [@name] - Neue Reparatur\n"
        f"/erledigt [ID] - Als erledigt markieren\n"
        f"/nichterledigt [ID] - Als nicht erledigt markieren\n"
        f"/aufgaben - Alle offenen Aufgaben"
    )

async def neue_aufgabe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Verwendung: /aufgabe Pumpe prüfen @max")
        return
    text = ' '.join(context.args)
    zugewiesen, text = finde_zuweisung(text)
    aufgabe = Aufgabe(beschreibung=text, zugewiesen_an=zugewiesen, kategorie='aufgabe')
    session.add(aufgabe)
    session.commit()
    antwort = f"✓ Aufgabe #{aufgabe.id} erstellt: {text}"
    if zugewiesen:
        antwort += f"\nZugewiesen an: {zugewiesen}"
    await update.message.reply_text(antwort)

async def neue_reparatur(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Verwendung: /reparatur Pumpe defekt @max")
        return
    text = ' '.join(context.args)
    zugewiesen, text = finde_zuweisung(text)
    aufgabe = Aufgabe(beschreibung=text, zugewiesen_an=zugewiesen, kategorie='reparatur')
    session.add(aufgabe)
    session.commit()
    antwort = f"🔧 Reparatur #{aufgabe.id} erstellt: {text}"
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
        aufgabe.erledigt_am = datetime.now()
        aufgabe.erledigt_von = update.effective_user.first_name
        session.commit()
        await update.message.reply_text(f"✓ Aufgabe #{aufgabe_id} als erledigt markiert!")
    except ValueError:
        await update.message.reply_text("Bitte eine gültige Nummer angeben!")

async def nicht_erledigt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Verwendung: /nichterledigt 5")
        return
    try:
        aufgabe_id = int(context.args[0])
        aufgabe = session.get(Aufgabe, aufgabe_id)
        if not aufgabe:
            await update.message.reply_text(f"Aufgabe #{aufgabe_id} nicht gefunden!")
            return
        aufgabe.erledigt = False
        aufgabe.erledigt_am = None
        aufgabe.erledigt_von = None
        session.commit()
        await update.message.reply_text(f"↩ Aufgabe #{aufgabe_id} wieder auf offen gesetzt!")
    except ValueError:
        await update.message.reply_text("Bitte eine gültige Nummer angeben!")

async def aufgaben_liste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    aufgaben = session.query(Aufgabe).filter_by(erledigt=False).all()
    if not aufgaben:
        await update.message.reply_text("Keine offenen Aufgaben!")
        return
    text = "📋 Offene Aufgaben:\n\n"
    for a in aufgaben:
        emoji = "🔧" if a.kategorie == 'reparatur' else "📌"
        text += f"{emoji} #{a.id} {a.beschreibung}"
        if a.zugewiesen_an:
            text += f" → {a.zugewiesen_an}"
        text += "\n"
    await update.message.reply_text(text)
