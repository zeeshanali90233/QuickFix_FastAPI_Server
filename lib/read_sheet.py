from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os

async def read_sheet(SAFilePath, spreadsheetId):
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

    credentials = Credentials.from_service_account_file(
        SAFilePath, scopes=SCOPES
    )

    try:
        service = build('sheets', 'v4', credentials=credentials)
        sheet = service.spreadsheets()

        # First, get the sheet metadata to find the number of rows
        metadata = sheet.get(spreadsheetId=spreadsheetId).execute()
        sheets = metadata.get('sheets', [])
        
        # Assuming you're working with the first sheet
        sheet_properties = sheets[0].get('properties', {})
        sheet_title = sheet_properties.get('title', 'Sheet1')
        
        # Get the last row that contains data
        range_response = sheet.values().get(spreadsheetId=spreadsheetId, range=f"{sheet_title}!A:A").execute()
        last_row_data = range_response.get('values', [])
        last_row = len(last_row_data)  # This gives the last row index with data

        # Define the dynamic range
        RANGE_NAME = f"{sheet_title}!A2:D{last_row}"  # Adjust as necessary

        # Fetch data from the specified dynamic range
        result = sheet.values().get(spreadsheetId=spreadsheetId, range=RANGE_NAME).execute()
        rows = result.get('values', [])

        if not rows:
            return {"message": "No data found."}

        return {"data": rows}
    except Exception as e:
        print(e)
        raise e
