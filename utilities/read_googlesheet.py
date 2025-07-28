import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# Define scope
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

# Path to your credentials file
creds = ServiceAccountCredentials.from_json_keyfile_name("D:\\BookNest\\utilities\\credentials.json", scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the Google Sheet by URL or title
sheet_url = "https://docs.google.com/spreadsheets/d/1WBAOPiIMEUuE0g30PUjHisoFlNpEDsdRmUjlPmkDnvI"
sheet = client.open_by_url(sheet_url)

# Select worksheet by name or index
worksheet = sheet.get_worksheet(0)  # or use .worksheet("Sheet1")

# Read all data as a list of lists
data = worksheet.get_all_values()

# Print the data
for row in data:
    print("================================\n")
    print(row)
 
# Get all rows as list of dicts (header must be present)
records = worksheet.get_all_records()

# Create JSON array from 'Title (English)' and 'Language' columns
json_array = []
cnt = 1
for row in records:
    if row.get("Title (English)") and row["Author/Publisher"]:
        print(row["Title (English)"])
        book = {}
        book["S.No"] = cnt
        cnt += 1
        if row.get("Title in language (If not English) "):
            book["Book Title"] = row["Title (English)"] + " (" + row["Title in language (If not English) "] + ")"
        else:    
            book["Book Title"] = row["Title (English)"]

        book["Author"] = row["Author/Publisher"]
        book["Rent / week"] = row["Expected Rent per week"]
        json_array.append(book)


# Print or write to file
print(json.dumps(json_array, indent=2, ensure_ascii=False))

# Optionally save to file
with open("csvjson.json", "w", encoding="utf-8") as f:
     json.dump(json_array, f, indent=2, ensure_ascii=False)