import telebot
import requests
import re
from datetime import datetime
from flask import Flask, request

# === Bot Setup ===
TOKEN = '7692838009:AAFp5tAXLJNY736aMR13LK3KJw3PdtrXP60'
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# === Google Apps Script URL ===
GAS_URL = 'https://script.google.com/macros/s/AKfycb.../exec'  # GANTI dengan milikmu

# === Pemetaan Kategori ===
cat_map = {
    "mistake": "MISTAKE", "crossbank": "CROSSBANK", "salah proses": "SALAH PROSES",
    "kurang proses": "KURANG PROSES", "lebih proses": "LEBIH PROSES",
    "lebih transfer": "LEBIH PROSES", "lebih kirim": "LEBIH PROSES",
    "double transfer": "DOUBLE TRANSFER", "double kirim": "DOUBLE TRANSFER"
}

@bot.message_handler(content_types=['text'])
def handle_mistake(message):
    if message.chat.type not in ["group", "supergroup"]:
        return

    text = message.text
    lines = text.splitlines()
    category = next((v for k, v in cat_map.items() if k in text.lower()), "")
    if not category:
        return

    data = {
        "username": "",
        "nama_mutasi": "",
        "nominal": "",
        "officer": "",
        "tiket": "",
        "asset": "",
        "category": category
    }

    for line in lines:
        l = line.lower()
        if "id" in l and ":" in line:
            data["username"] = line.split(":", 1)[-1].strip()
        elif "mutasi" in l and ":" in line:
            data["nama_mutasi"] = line.split(":", 1)[-1].strip().title()
        elif "nominal" in l and ":" in line:
            raw = re.sub(r"[^\d]", "", line.split(":", 1)[-1])
            if raw:
                data["nominal"] = f"Rp {int(raw):,}".replace(",", ".")
        elif "officer" in l and ":" in line:
            data["officer"] = line.split(":", 1)[-1].strip()
        elif "tiket" in l and ":" in line:
            data["tiket"] = line.split(":", 1)[-1].strip()
        elif "asset" in l and ":" in line:
            data["asset"] = line.split(":", 1)[-1].strip().upper()

    now = datetime.now()
    data["tanggal"] = now.strftime("%d-%m-%Y")
    data["jam"] = now.strftime("%H:%M:%S")

    if all([data["username"], data["nama_mutasi"], data["nominal"], data["officer"], data["tiket"], data["asset"]]):
        try:
            res = requests.post(GAS_URL, json=data)
            if res.status_code == 200:
                bot.reply_to(message, f"✅ {category} sudah saya catat capt @FernandooFzz @Gustom138, lain kali hati-hati ya.")
            else:
                bot.reply_to(message, "⚠️ Gagal kirim ke spreadsheet.")
        except Exception as e:
            bot.reply_to(message, f"❌ Error: {e}")
    else:
        bot.reply_to(message, (
            "⚠️ Format tidak lengkap. Harap isi sebagai berikut:\n"
            "USERNAME / ID : \nNAMA MUTASI : \nNominal : \nOfficer : \nTiket : \nAsset :"
        ))

# === Webhook Endpoint ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return "Bot Mistake aktif!", 200

# === Mulai Aplikasi Flask (port 8080) ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
