import os
import telebot
from flask import Flask, request
import requests
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None  # Jika modul zoneinfo tidak tersedia

# Ambil token bot dan URL GAS dari Environment Variables
TOKEN = os.environ.get('BOT_MISTAKE_TOKEN')
GAS_URL = os.environ.get('BOT_MISTAKE_GAS_URL')

if not TOKEN or not GAS_URL:
    raise RuntimeError("Environment variable BOT_MISTAKE_TOKEN atau BOT_MISTAKE_GAS_URL belum diset")

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Daftar kategori yang akan difilter
cat_map = ["mistake", "crossbank", "salah proses", "kurang proses", "lebih proses", "double transfer"]

@bot.message_handler(content_types=['text'])
def handle_text(message):
    # Hanya proses pesan teks di grup (abaikan pesan pribadi)
    if message.chat.type not in ['group', 'supergroup']:
        return

    text = message.text.strip()
    data = parse_message(text)
    if not data:
        # Format pesan tidak sesuai
        bot.reply_to(message, "Format pesan tidak sesuai. Pastikan menggunakan format: ID, Mutasi, Nominal, Officer, Tiket, Asset.")
        return

    # Tentukan kategori berdasarkan kata kunci di pesan
    category = None
    lower_text = text.lower()
    for cat in cat_map:
        if cat in lower_text:
            category = cat
            break
    if not category:
        category = "mistake"  # kategori default

    # Siapkan payload JSON untuk dikirim ke Google Apps Script
    now = datetime.now(ZoneInfo("Asia/Jakarta")) if ZoneInfo else datetime.now()
    tanggal = now.strftime("%Y-%m-%d")
    jam = now.strftime("%H:%M:%S")
    username = message.from_user.username or message.from_user.first_name

    payload = {
        "tanggal": tanggal,
        "jam": jam,
        "username": username,
        "nama_mutasi": data.get("mutasi", ""),
        "nominal": data.get("nominal", ""),
        "officer": data.get("officer", ""),
        "tiket": data.get("tiket", ""),
        "asset": data.get("asset", ""),
        "category": category
    }

    try:
        response = requests.post(GAS_URL, json=payload, timeout=5)
        if response.status_code == 200:
            bot.reply_to(message, "Data berhasil dikirim.")
        else:
            bot.reply_to(message, f"Gagal mengirim data (status code {response.status_code}).")
    except Exception as e:
        bot.reply_to(message, f"Terjadi kesalahan saat mengirim data: {e}")

def parse_message(text):
    """
    Mengekstrak field ID, Mutasi, Nominal, Officer, Tiket, Asset dari teks pesan.
    Mengembalikan dict {id, mutasi, nominal, officer, tiket, asset} jika sukses, atau None jika format salah.
    """
    import re
    # Pola regex untuk mencocokkan format pesan (case-insensitive)
    # Memungkinkan pemisah berupa spasi, koma, atau newline antar field.
    sep_pattern = r'(?:[\s;]|,(?!\d))+'
    pattern = rf'ID\s*[:\-]\s*(?P<id>[\s\S]+?){sep_pattern}' \
              rf'Mutasi\s*[:\-]\s*(?P<mutasi>[\s\S]+?){sep_pattern}' \
              rf'Nominal\s*[:\-]\s*(?P<nominal>[\s\S]+?){sep_pattern}' \
              rf'Officer\s*[:\-]\s*(?P<officer>[\s\S]+?){sep_pattern}' \
              rf'Tiket\s*[:\-]\s*(?P<tiket>[\s\S]+?){sep_pattern}' \
              rf'Asset\s*[:\-]\s*(?P<asset>[\s\S]+?)\s*$'
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    # Membersihkan spasi/koma di ujung setiap nilai field
    fields = {k: v.strip().rstrip(',;') for k, v in match.groupdict().items()}
    return fields

# Route webhook Telegram (untuk menerima update)
@app.route('/' + TOKEN, methods=['POST'])
def telegram_webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

# Route index sederhana (untuk pengecekan)
@app.route('/', methods=['GET'])
def index():
    return "Bot Mistake aktif", 200

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 0))
    if port == 0:
        # Mode lokal: gunakan polling
        print("Bot berjalan dalam mode polling.")
        bot.remove_webhook()
        bot.infinity_polling()
    else:
        # Mode produksi (Railway): gunakan webhook
        print(f"Bot berjalan dalam mode webhook di port {port}.")
        bot.remove_webhook()
        # Atur webhook otomatis jika URL publik disediakan di env
        webhook_url = os.environ.get('WEBHOOK_URL')
        if webhook_url:
            webhook_url = webhook_url.rstrip('/')
bot.remove_webhook()
exit()  # langsung keluar agar Railway tidak jalan

            bot.set_webhook(url=f"{webhook_url}/{TOKEN}")
            print(f"Webhook diatur ke {webhook_url}/{TOKEN}")
        app.run(host="0.0.0.0", port=port)

Commit message: Deploy bot mistake ke Railway (final)
