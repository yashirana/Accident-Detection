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

app = Flask(__name__)
bootstrap = Bootstrap(app)  

model_json_file = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\model.json"
model_weights_file = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\model_weights.h5"
video_path = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\Demo2.mp4"  # Update with your video file path
save_directory = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\accident detected"  # Update with your save directory
spreadsheet_id = "1Bd0BkDw0fzBD1tB2f6WvpE4E6UxG_hADqY6o650i7cA"  # Update with your spreadsheet ID
range_name = "Sheet1!A:H"  # Update with the correct sheet name and range
# bot_token = "6464904338:AAGZgrNECVisxgKryybFkqZ530bMU9FgIiI"  # Update with your Telegram bot token
# chat_id = "1210549392"  # Update with your Telegram chat ID


if not os.path.exists(model_json_file):
    print(f"Error: '{model_json_file}' not found.")
    exit()

if not os.path.exists(model_weights_file):
    print(f"Error: '{model_weights_file}' not found.")      
    exit()

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
    credentials = service_account.Credentials.from_service_account_file(
        r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\graph-388510-b8eef180584d.json",  # Update with your service account JSON file path
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
    app.run(debug=True)