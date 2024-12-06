import cv2
import face_recognition
import numpy as np
import pandas as pd
import os
from pymongo import MongoClient
import sys

def func1(video_path, session_id):
    print("func1 started")
    client = MongoClient('mongodb://localhost:27017/')
    db = client['attendance']
    collection = db['recognized_faces']
    print("mongoStarted")

    known_face_encodings = []
    known_face_names = []
    recognized_faces = []

    known_people_dir = 'images'
    for image_name in os.listdir(known_people_dir):
        image_path = os.path.join(known_people_dir, image_name)
        image = face_recognition.load_image_file(image_path)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(encoding)
        name = os.path.splitext(image_name)[0]
        known_face_names.append(name)
    print("encodingDone")

    video_capture = cv2.VideoCapture(video_path)
    print("videoStarted")
    while video_capture.isOpened():
        ret, frame = video_capture.read()
        if not ret:
            break

        rgb_frame = np.array(frame[:, :, ::-1])
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = ""
            face_distance = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distance)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                if name not in recognized_faces:
                    recognized_faces.append(name)
                    collection.insert_one({'name': name, 'session_id': session_id})
                    print(f"Saved {name} to MongoDB with session ID {session_id}")

    print("videoFinished")
    video_capture.release()
    recognized_faces = list(set(recognized_faces))
    df = pd.DataFrame(recognized_faces, columns=['Name'])
    df.to_csv("output.csv", index=False)
    print("savedToCSV")
    print("Recognized faces saved to CSV and MongoDB.")


    
video_path = sys.argv[1]
session_id = sys.argv[2]
func1(video_path, session_id)
