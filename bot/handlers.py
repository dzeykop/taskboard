import yaml
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import Aufgabe, session

AUFGABE_TEXT, AUFGABE_NAME = range(2)
REPARATUR_TEXT, REPARATUR_NAME = range(2, 4)
ERLEDIGT_WAHL = range(4, 5)
NICHTERLEDIGT_WAHL = range(5, 6)

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

def offene_aufgaben_buttons():
    aufgaben = session.query(Aufgabe).filter_by(erledigt=False).all()
    if not aufgaben:
        return None
    buttons = []
    for a in aufgaben:
        emoji = "🔧" if a.kategorie == 'reparatur' else "📌"
        label = f"{emoji} #{a.id} {a.beschreibung[:30]}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"erl_{a.id}")])
    return InlineKeyboardMarkup(buttons)

def erledigte_aufgaben_buttons():
    aufgaben = session.query(Aufgabe).filter_by(erledigt=True).all()
    if not aufgaben:
        return None
    buttons = []
    for a in aufgaben:
        emoji = "🔧" if a.kategorie == 'reparatur' else "📌"
        label = f"{emoji} #{a.id} {a.beschreibung[:30]}"
        buttons.append([InlineKeyboardButton(label, callback_data=f"nierl_{a.id}")])
    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Hallo {user.first_name}!\n"
        f"Deine Telegram-ID: {user.id}\n\n"
        f"Befehle:\n"
        f"/aufgabe - Neue Aufgabe erstellen\n"
        f"/reparatur - Neue Reparatur erstellen\n"
        f"/erledigt - Aufgabe als erledigt markieren\n"
        f"/nichterledigt - Aufgabe zurücksetzen\n"
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

# --- ERLEDIGT ---
async def erledigt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = offene_aufgaben_buttons()
    if not buttons:
        await update.message.reply_text("Keine offenen Aufgaben!")
        return ConversationHandler.END
    await update.message.reply_text("Welche Aufgabe ist erledigt?", reply_markup=buttons)
    return ERLEDIGT_WAHL

async def erledigt_wahl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    aufgabe_id = int(query.data.replace("erl_", ""))
    aufgabe = session.get(Aufgabe, aufgabe_id)
    if aufgabe:
        aufgabe.erledigt = True
        aufgabe.erledigt_am = datetime.now()
        aufgabe.erledigt_von = query.from_user.first_name
        session.commit()
        await query.edit_message_text(f"✓ Aufgabe #{aufgabe_id} als erledigt markiert!")
    return ConversationHandler.END

# --- NICHT ERLEDIGT ---
async def nichterledigt_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = erledigte_aufgaben_buttons()
    if not buttons:
        await update.message.reply_text("Keine erledigten Aufgaben!")
        return ConversationHandler.END
    await update.message.reply_text("Welche Aufgabe zurücksetzen?", reply_markup=buttons)
    return NICHTERLEDIGT_WAHL

async def nichterledigt_wahl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    aufgabe_id = int(query.data.replace("nierl_", ""))
    aufgabe = session.get(Aufgabe, aufgabe_id)
    if aufgabe:
        aufgabe.erledigt = False
        aufgabe.erledigt_am = None
        aufgabe.erledigt_von = None
        session.commit()
        await query.edit_message_text(f"↩ Aufgabe #{aufgabe_id} wieder auf offen gesetzt!")
    return ConversationHandler.END

async def abbrechen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Abgebrochen.")
    return ConversationHandler.END

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
