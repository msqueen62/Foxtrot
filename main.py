import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Scope akses untuk Google Sheets dan Drive
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Ambil JSON kredensial dari ENV
json_str = os.environ.get("GOOGLE_CREDS")

# Validasi: kalau kosong, langsung berhenti
if not json_str:
    raise Exception("Environment variable GOOGLE_CREDS tidak ditemukan!")

# Parsing string ke dict
creds_dict = json.loads(json_str)

# Gunakan dict sebagai kredensial
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

# Authorize dengan gspread
client = gspread.authorize(creds)
