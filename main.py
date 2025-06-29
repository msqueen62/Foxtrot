import os
import json
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Ambil JSON kredensial dari ENV
json_str = os.environ.get("GOOGLE_CREDENTIALS_JSON")

# Parsing string ke dict
creds_dict = json.loads(json_str)

# Gunakan dict sebagai kredensial
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
