import yaml
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Aufgabe, session

AUFGABE_TEXT, AUFGABE_NAME = range(2)
REPARATUR_TEXT, REPARATUR_NAME = range(2, 4)

def lade_mitarbeiter():
    with open('/opt/taskboard/config/mitarbeiter.yaml', 'r') as f:
        return yaml.safe_load(f)['mitarbeiter']

def mitarbeiter_buttons():
    mitarbeiter = lade_mitarbeiter()
    buttons = []
    row = []
    for i, m in enumerate(mitarbeiter):
        vorname = m['name'].split()[0]
        row.append(InlineKeyboardButton(vorname, callback_data=f"name_{m['name']}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton("Niemand", callback_data="name_keine")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hallo {user.first_name}!\n"
        f"Deine Telegram-ID: {user.id}\n\n"
        f"Befehle:\n"
        f"/aufgabe - Neue Aufgabe erstellen\n"
        f"/reparatur - Neue Reparatur erstellen\n"
        f"/erledigt [ID] - Als erledigt markieren\n"
        f"/nichterledigt [ID] - Als nicht erledigt markieren\n"
        f"/aufgaben - Alle offenen Aufgaben"
    )

# --- AUFGABE ---
async def aufgabe_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Beschreibe die Aufgabe:")
    return AUFGABE_TEXT

async def aufgabe_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['aufgabe_text'] = update.message.text
    context.user_data['aufgabe_kategorie'] = 'aufgabe'
    await update.message.reply_text("👤 Wer soll das machen?", reply_markup=mitarbeiter_buttons())
    return AUFGABE_NAME

async def aufgabe_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    zugewiesen = None if query.data == "name_keine" else query.data.replace("name_", "")
    text = context.user_data['aufgabe_text']
    kategorie = context.user_data['aufgabe_kategorie']
    aufgabe = Aufgabe(beschreibung=text, zugewiesen_an=zugewiesen, kategorie=kategorie)
    session.add(aufgabe)
    session.commit()
    antwort = f"✓ Aufgabe #{aufgabe.id} erstellt: {text}"
    if zugewiesen:
        antwort += f"\nZugewiesen an: {zugewiesen}"
    await query.edit_message_text(antwort)
    return ConversationHandler.END

# --- REPARATUR ---
async def reparatur_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔧 Beschreibe die Reparatur:")
    return REPARATUR_TEXT

async def reparatur_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['aufgabe_text'] = update.message.text
    context.user_data['aufgabe_kategorie'] = 'reparatur'
    await update.message.reply_text("👤 Wer soll das machen?", reply_markup=mitarbeiter_buttons())
    return REPARATUR_NAME

async def reparatur_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    zugewiesen = None if query.data == "name_keine" else query.data.replace("name_", "")
    text = context.user_data['aufgabe_text']
    kategorie = context.user_data['aufgabe_kategorie']
    aufgabe = Aufgabe(beschreibung=text, zugewiesen_an=zugewiesen, kategorie=kategorie)
    session.add(aufgabe)
    session.commit()
    antwort = f"🔧 Reparatur #{aufgabe.id} erstellt: {text}"
    if zugewiesen:
        antwort += f"\nZugewiesen an: {zugewiesen}"
    await query.edit_message_text(antwort)
    return ConversationHandler.END

async def abbrechen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Abgebrochen.")
    return ConversationHandler.END

# --- ERLEDIGT / NICHT ERLEDIGT ---
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
