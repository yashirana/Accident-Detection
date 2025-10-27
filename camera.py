from flask import Flask, render_template
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

model_json_file = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\model.json"
model_weights_file = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\model_weights.h5"

# bot_token = "6464904338:AAGZgrNECVisxgKryybFkqZ530bMU9FgIiI"  # Update with your Telegram bot token
# chat_id = "1210549392"  # Update with your Telegram chat ID


# Function to authenticate with Google Sheets API
def authenticate_google_sheets():
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    credentials = service_account.Credentials.from_service_account_file(
        r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\graph-388510-b8eef180584d.json",  # Update with your service account JSON file path
        scopes=scopes
    )
    service = build('sheets', 'v4', credentials=credentials)
    return service

# Function to write data to Google Sheet
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


# def send_telegram_message(bot, chat_id, message):
#     try:
#         bot.send_message(chat_id, message)
#     except Exception as e:
#         print("An error occurred while sending Telegram message:", e)

# bot = telebot.TeleBot(bot_token)

# Function to start application
def start_application(video_path, save_directory, spreadsheet_id, range_name):
    
    # Initialize Accident Detection Model
    model = AccidentDetectionModel("model.json", 'model_weights.h5')
    font = cv2.FONT_HERSHEY_SIMPLEX

    # Sample data
    severity_data = ["Grievous Injury", "Fatal", "Damage Only"]
    collision_type_data = ["Drowned", "Hit fixed object", "Hit and Run", "Head on", "Hit animal"]
    road_character_data = ["Curve", "Others", "Not Applicable"]
    surface_condition_data = ["Dry", "Not Applicable"]
    weather_data = ["Clear", "Light Rain", "Fine"]

    # Sample location data
    location_addresses = [
        "AMINAGADA TO BAGALKOT SH-20 ROAD NEAR TIPPANNA GOUDAR FIELED",
        "SHIRUR AMINAGAD SH-20 ROAD NEAR KAMATAGI",
        "AMINAGAD BAGALKOT SH-20 NEAR BANATHIKOLL",
        "AMINAGAD BAGALKOT SH-20 ROAD NEAR ADILSHA HOTELA",
        "AMD TO BGK SH-20 ROAD NEAR AMINAGAD SULEBAVI CROSS",
        "Sample Location Address 1",
        "Sample Location Address 2"
    ]

    location_coordinates = [
        "16.363747 75.649473",
        "16.353417 75.555515",
        "16.24771 75.620478",
        "16.251731 75.520676",
        "16.401354 75.68946",
        "Sample Location Coordinate 1",
        "Sample Location Coordinate 2"
    ]

    # Authenticate with Google Sheets API
    service = authenticate_google_sheets()

    # Open the video
    video = cv2.VideoCapture(video_path)

    # Get video details
    fps = int(video.get(cv2.CAP_PROP_FPS))
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Create video writer for saving clips
    video_writer = None
    clip_counter = 1

    last_write_time = time.time()
    last_clip_save_time = time.time()

    while True:
        ret, frame = video.read()
        if not ret:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        roi = cv2.resize(gray_frame, (250, 250))

        pred, prob = model.predict_accident(roi[np.newaxis, :, :])
        if pred == "Accident":
            prob_percentage = round(prob[0][0] * 100, 2)

            cv2.rectangle(frame, (0, 0), (280, 40), (0, 0, 0), -1)
            cv2.putText(frame, f"{pred} {prob_percentage}", (20, 30), font, 1, (255, 255, 0), 2)

            # Sample random data
            severity = random.choice(severity_data)
            collision_type = random.choice(collision_type_data)
            road_character = random.choice(road_character_data)
            surface_condition = random.choice(surface_condition_data)
            weather = random.choice(weather_data)
            location_address = random.choice(location_addresses)
            location_coordinate = random.choice(location_coordinates)

            # Save video clip when accident probability is greater than 99% or every 10 seconds
            if prob_percentage > 99 or time.time() - last_clip_save_time >= 10:
                if video_writer is None:
                    clip_name = f"accident_detected_{clip_counter}.avi"
                    clip_path = os.path.join(save_directory, clip_name)
                    video_writer = cv2.VideoWriter(clip_path, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

                video_writer.write(frame)
                last_clip_save_time = time.time()

                # Write data to Google Sheet including "Accident Detected"
                if time.time() - last_write_time >= 5:
                    data = ["Accident Detected", severity, collision_type, road_character, surface_condition, weather, location_address, location_coordinate]
                    write_to_google_sheet(service, spreadsheet_id, range_name, data)
                    last_write_time = time.time()

        if cv2.waitKey(100) & 0xFF == ord('q'):
            break

        cv2.imshow('Video', frame)

    # Release resources
    if video_writer is not None:
        video_writer.release()

    video.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_path = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\Demo2.mp4"  # Update with your video file path
    save_directory = r"D:\Karnataka_project\Accident-Detection-System-main\Accident-Detection-System-main\accident detected"  # 
    spreadsheet_id = "1Bd0BkDw0fzBD1tB2f6WvpE4E6UxG_hADqY6o650i7cA"  # Update with your spreadsheet ID
    range_name = "Sheet1!A:H"  # Update with the correct sheet name and range
    start_application(video_path, save_directory, spreadsheet_id, range_name)

