from flask import Flask, render_template, jsonify
import cv2
from detection import AccidentDetectionModel
import numpy as np
import os
from flask_bootstrap import Bootstrap
import random
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import telebot
import tempfile

app = Flask(__name__)
bootstrap = Bootstrap(app)

# Configuration via environment variables (suitable for container/cloud deploy)
model_json_file = os.environ.get("MODEL_JSON", "model.json")
model_weights_file = os.environ.get("MODEL_WEIGHTS", "model_weights.h5")
video_path = os.environ.get("VIDEO_PATH", "Demo2.mp4")
save_directory = os.environ.get("SAVE_DIR", "accident detected")
spreadsheet_id = os.environ.get("GOOGLE_SHEET_ID", os.environ.get("SPREADSHEET_ID", None))
range_name = os.environ.get("SHEET_RANGE", "Sheet1!A:H")
# Optional Telegram
bot_token = os.environ.get("TELEGRAM_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

# Optionally provide service-account JSON as the full JSON string in the
# SERVICE_ACCOUNT_JSON env var. If provided, write to a temp file and use it.
service_account_json = os.environ.get("SERVICE_ACCOUNT_JSON")
service_account_path = None
if service_account_json:
    fd, service_account_path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        f.write(service_account_json)


# def send_telegram_message(bot, chat_id, message):
#     try:
#         bot.send_message(chat_id, message)
#     except Exception as e:
#         print("An error occurred while sending Telegram message:", e)

# bot = telebot.TeleBot(bot_token)

model = AccidentDetectionModel(model_json_file, model_weights_file)
font = cv2.FONT_HERSHEY_SIMPLEX

def authenticate_google_sheets():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    # Prefer SERVICE_ACCOUNT_JSON written to a temp file (service_account_path).
    # Fallback to SERVICE_ACCOUNT_FILE env var if provided and points to an existing file.
    creds_file = None
    if service_account_path and os.path.exists(service_account_path):
        creds_file = service_account_path
    else:
        sa_file_env = os.environ.get("SERVICE_ACCOUNT_FILE")
        if sa_file_env and os.path.exists(sa_file_env):
            creds_file = sa_file_env

    if not creds_file:
        raise RuntimeError("No service account JSON found. Set SERVICE_ACCOUNT_JSON or SERVICE_ACCOUNT_FILE env var.")

    credentials = service_account.Credentials.from_service_account_file(
        creds_file,
        scopes=scopes
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service

def write_to_google_sheet(service, spreadsheet_id, range_name, data):
    try:
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body={"values": [data]}
        ).execute()
        

        print("Data:", data) 

    except Exception as e:
        print("An error occurred while writing to Google Sheet:", e)


@app.route('/detect_accident')
def detect_accident():
    video = cv2.VideoCapture(video_path)  # for camera use video = cv2.VideoCapture(0)
        # Sample data
    severity_data = ["Grievous Injury", "Fatal", "Damage Only"]
    collision_type_data = ["Drowned", "Hit fixed object", "Hit and Run", "Head on", "Hit animal"]
    road_character_data = ["Curve", "Others", "Not Applicable"]
    surface_condition_data = ["Dry", "Not Applicable"]
    weather_data = ["Clear", "Light Rain", "Fine"]

    # Sample location data
    location_addresses = [
        "Kalidas Road", 
        "Hospital Road",   
        "MS Building Park", 
        "Venkatappa Art Gallery",
        "Jawahar Bal Bhavan",
    ]

    location_coordinates = [
        [77.5816986734381, 12.979567234934038],
        [77.57749376988772, 12.973224980690162],
        [77.58769224146204, 12.978411587631172],
        [77.59539535205039, 12.97380930189287],
        [77.59842946492148, 12.976759610007619],
    ]

    # Authenticate with Google Sheets API
    # service = authenticate_google_sheets()

    # Open the video
    video = cv2.VideoCapture(video_path)

    # Get video details
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    while True:
        ret, frame = video.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        roi = cv2.resize(gray_frame, (250, 250))

# Sample random data
        severity = f"Severity of Data : {random.choice(severity_data)}"
        collision_type = f"Collision type : {random.choice(collision_type_data)}"
        road_character = f"Road Character : {random.choice(road_character_data)}"
        surface_condition = f"Surface Condition : {random.choice(surface_condition_data)}"
        weather = f"Weather : {random.choice(weather_data)}"
        location_address = f"Location Address : {random.choice(location_addresses)}"
        location_coordinate = f"Location Coordinate : {random.choice(location_coordinates)}"
        
        telegram_message = "Accident Detected!\nSeverity: {}\nCollision Type: {}\nRoad Character: {}\nSurface Condition: {}\nWeather: {}\nLocation Address: {}\nLocation Coordinate: {}".format(severity, collision_type, road_character, surface_condition, weather, location_address,location_coordinate)
        # send_telegram_message(bot, chat_id, telegram_message)

        pred, prob = model.predict_accident(roi[np.newaxis, :, :])
        
        if pred == "Accident":
            prob_percentage = round(prob[0][0] * 100, 2)
            detection_info = f"Accident detected with probability: {prob_percentage}%"
            data = [detection_info, severity, collision_type, road_character, surface_condition, weather, location_address, location_coordinate]
            formatted_data = ', '.join(map(str, data))
            final_data = '\n'.join(formatted_data.split(', '))
            # write_to_google_sheet(service, spreadsheet_id, range_name, data)
            return final_data # This will stop the video processing and return the detection info
    video.release()
    cv2.destroyAllWindows()


@app.route('/')
def index():
    return render_template('./index1.html')

@app.route('/about')
def about():
    about_data = detect_accident()
    
    return render_template('about.html', data=about_data)



if __name__ == '__main__':
    # Use PORT env var if provided (Cloud Run sets this automatically)
    port = int(os.environ.get('PORT', 8080))
    debug_flag = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug_flag)