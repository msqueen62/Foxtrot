import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Lokasi file yang di-upload via Secret Files (Render otomatis meletakkan di path ini)
path_to_creds = "/etc/secrets/creds.json"

creds = ServiceAccountCredentials.from_json_keyfile_name(path_to_creds, scope)
client = gspread.authorize(creds)
