import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# --- Setup Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
path_to_creds = "/etc/secrets/creds.json"  # Lokasi Secret File di Render

creds = ServiceAccountCredentials.from_json_keyfile_name(path_to_creds, scope)
client = gspread.authorize(creds)

# Buka spreadsheet dan worksheet tertentu
sheet = client.open("06. JUNE 2025 LIST SUNTIK DANA WD").worksheet("FOXTROT")

# --- Setup Bot Telegram ---
TOKEN = os.environ.get("TOKEN")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

def start(update, context):
    update.message.reply_text("Bot aktif. Kirim pesan untuk mencatat data.")

def handle_message(update, context):
    text = update.message.text
    update.message.reply_text(f"Pesan diterima: {text}")
    # Contoh menulis ke Sheet
    sheet.append_row([text])

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# Jalankan polling
updater.start_polling()
updater.idle()
