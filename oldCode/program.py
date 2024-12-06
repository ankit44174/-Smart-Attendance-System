import threading
import time
from datetime import datetime
import face_recognition
import cv2
import numpy as np
import csv
import os

# Shared variable and lock
current_time = None
time_lock = threading.Lock()


####################################################################################################################################




video_capture = cv2.VideoCapture(0)


# ankit_img = face_recognition.load_image_file("attendanceFaceRecognition/photos/Ankit.jpg")
# ankit_encoding = face_recognition.face_encodings(ankit_img)[0]

# prince_img = face_recognition.load_image_file('attendanceFaceRecognition/photos/prince.jpg')
# prince_encoding = face_recognition.face_encodings(prince_img)[0]

# atul_img = face_recognition.load_image_file('attendanceFaceRecognition/photos/Atul.jpg')
# atul_encoding = face_recognition.face_encodings(atul_img)[0]

# known_face_encodings = [
#     ankit_encoding,
#     prince_encoding,
#     atul_encoding
# ]

# known_face_names = [
#     'Ankit',
#     'Prince',
#     'Atul'
# ]

known_face_encodings = []
known_face_names = []

    # Directory where your training images are stored
known_people_dir = 'images'

    # Load each image in the training directory
for image_name in os.listdir(known_people_dir):
    image_path = os.path.join(known_people_dir, image_name)
        # Load the image using face_recognition
    image = face_recognition.load_image_file(image_path)
        # Get the face encodings for the first face in the image
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)
        # Extract the name from the image filename (assumes format 'name.jpg')
    name = os.path.splitext(image_name)[0]
    known_face_names.append(name)

students = known_face_names.copy()

face_locations = []
face_encodings = []
face_names = []
s = True

now = datetime.now()
curr_date = now.strftime("%Y-%m-%d")


# f = open(curr_date + '.csv','a', newline='')
# lnwriter = csv.writer(f)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')



#####################################################################################################################################
stop_event = threading.Event() 

# Function for the first loop: fetches current time
def fetch_time():
    global current_time
    while not stop_event.is_set():
        with time_lock:
            current_time = time.strftime("%H:%M:%S", time.localtime())
        time.sleep(1)  # Wait for 1 second before fetching the time again

# Function for the second loop: accesses and prints the time
def access_time():
    while not stop_event.is_set():
        with time_lock:
            # print(f"Current Time: {current_time}")
            poi,frame = video_capture.read()
            small_frame = cv2.resize(frame,(0,0),fx = 0.25 , fy = 0.25)
            rgb_small_frame = np.array(small_frame[:,:,::-1])

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

            


            if s:
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame,face_locations)
                face_names = []
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                # Use the known face with the smallest distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                    best_match_index = np.argmin(face_distances)

                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                # Draw a box around the face
                    # cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

                # Draw a label with a name below the face
                    cv2.putText(frame, name, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)            
                for face_encoding in face_encodings:
                    matches = face_recognition.compare_faces(known_face_encodings,face_encoding)
                    name = ""
                    face_distance = face_recognition.face_distance(known_face_encodings,face_encoding)
                    best_match_index = np.argmin(face_distance)
                    if matches[best_match_index]:
                        name = known_face_names[best_match_index]

                    face_names.append(name)
                    if name in known_face_names:
                        if name in students:
                            print(name)

                            students.remove(name)
                            # print(students)
                            # curr_time = now.strftime("%H-%M-%S")
                            
                            f = open(curr_date + '.csv','a', newline='')
                            lnwriter = csv.writer(f)
                            lnwriter.writerow([name,current_time])


        cv2.imshow("Attendacnce System",frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break   

            
        time.sleep(1)  # Simulate some processing time
    video_capture.release()
    cv2.destroyAllWindows()
    f.close()


def main():


    # Creating and starting threads
    thread1 = threading.Thread(target=fetch_time)
    thread2 = threading.Thread(target=access_time)

    thread1.start()
    thread2.start()


    cmd = input("")

    if  cmd == "stop":
        stop_event.set()

    # Joining threads (optional, if you want the main program to wait for these threads to finish)
    thread1.join()
    thread2.join()
