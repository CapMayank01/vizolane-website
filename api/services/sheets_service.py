import os
from datetime import datetime
import pytz
from google.oauth2 import service_account
from googleapiclient.discovery import build

sheets_client = None


def init_sheets():
    global sheets_client
    try:
        credentials_path = os.path.abspath(
            os.getenv("GOOGLE_CREDENTIALS_PATH") or "./credentials.json"
        )

        if not os.path.exists(credentials_path):
            print(f"[WARNING]  Google credentials file not found at {credentials_path}")
            return False

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = service_account.Credentials.from_service_account_file(
            credentials_path, scopes=scopes
        )
        sheets_client = build("sheets", "v4", credentials=creds)
        print("[SUCCESS] Google Sheets service ready")
        return True
    except Exception as e:
        print(f"[ERROR] Google Sheets init failed: {e}")
        return False


def append_contact_to_sheet(data):
    global sheets_client
    if not sheets_client:
        msg = "[WARNING]  Sheets client not initialized — skipping sheet write."
        print(msg)
        raise ValueError(msg)

    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not sheet_id:
        msg = "[WARNING]  GOOGLE_SHEET_ID not set — skipping sheet write."
        print(msg)
        raise ValueError(msg)

    tz = pytz.timezone("Asia/Kolkata")
    timestamp = datetime.now(tz).strftime("%d/%m/%Y, %I:%M:%S %p")

    name = data.get("name", "")
    email = data.get("email", "")
    phone = data.get("phone", "") or "N/A"
    message = data.get("message", "")

    values = [[timestamp, name, email, phone, message, "New"]]
    body = {"values": values}

    try:
        result = (
            sheets_client.spreadsheets()
            .values()
            .append(
                spreadsheetId=sheet_id,
                range="Sheet1!A:F",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body=body,
            )
            .execute()
        )
        print(f"[SUCCESS] Contact appended to Google Sheet: {result.get('updates', {}).get('updatedRange')}")
        return result
    except Exception as e:
        print(f"[ERROR] Failed to write to Google Sheet: {e}")
        raise e
