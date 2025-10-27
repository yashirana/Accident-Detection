from flask import Flask, render_template

import gspread
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

@app.route('/')
def index():
    # Define the scope and credentials
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('graph-388510-97035485b759.json', scope)

    # Authorize the client
    client = gspread.authorize(creds)

    # Open the spreadsheet
    sheet = client.open('graph').sheet1  # Replace 'Your Spreadsheet Name' with your actual spreadsheet name

    # Get all records from the spreadsheet
    records = sheet.get_all_records()

    # Render the HTML template and pass the records to it
    return render_template('analytics.html', records=records)

if __name__ == '__main__':
    app.run(debug=True)
