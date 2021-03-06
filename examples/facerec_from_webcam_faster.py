import face_recognition
import cv2
import http
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
from socketserver import ThreadingMixIn
import threading

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)

video_capture = cv2.VideoCapture("http://192.168.0.99/live/0/mjpeg.jpg?basic=YWRtaW46aG9zcGl0YWxpdHk=")
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
video_writer  = cv2.VideoWriter('output.avi', fourcc, 20.0, (1280,720))

# Load a sample picture and learn how to recognize it.
adi_image = face_recognition.load_image_file("adi.jpg")
adi_face_encoding = face_recognition.face_encodings(adi_image,known_face_locations=None, num_jitters=10)[0]

ards_image = face_recognition.load_image_file("ards.jpg")
ards_face_encoding = face_recognition.face_encodings(ards_image,known_face_locations=None, num_jitters=10)[0]

chiara_image = face_recognition.load_image_file("chiara.jpg")
chiara_face_encoding = face_recognition.face_encodings(chiara_image,known_face_locations=None, num_jitters=10)[0]

junel_image = face_recognition.load_image_file("junel.jpg")
junel_face_encoding = face_recognition.face_encodings(junel_image,known_face_locations=None, num_jitters=10)[0]

john_image = face_recognition.load_image_file("john.jpg")
john_face_encoding = face_recognition.face_encodings(john_image,known_face_locations=None, num_jitters=10)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    adi_face_encoding,
    ards_face_encoding,
    chiara_face_encoding,
    junel_face_encoding,
    john_face_encoding
]
known_face_names = [
    "Adi",
    "Ards",
    "Chiara",
    "Junel",
    "John"
]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
face_isrecog = []
process_this_frame = True

server_started = False
server = ThreadedHTTPServer(('192.168.0.254', 8085), CamHandler)
server.serve_forever()

while True:
    # Grab a single frame of video  
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        face_isrecog = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance= 0.5)
            name = "Unknown"
            isrecog = False

            # If a match was found in known_face_encodings, just use the first one.
            if True in matches:
                first_match_index = matches.index(True)
                name = known_face_names[first_match_index]
                isrecog = True

            face_names.append(name)
            face_isrecog.append(isrecog)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name, isrecog in zip(face_locations, face_names, face_isrecog):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 2
        right *= 2
        bottom *= 2
        left *= 2

        # Draw a box around the face
        bcolor = (255,255,255)
        if isrecog:
            bcolor = (0, 255, 0)
        else:
            bcolor = (0, 0, 255)

        cv2.rectangle(frame, (left, top - 10), (right, bottom + 10), bcolor, 1)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom + 40), (right, bottom + 10), bcolor, cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom + 40 - 8), font, 0.8, (255, 255, 255), 1)

    # Display the resulting image
    video_writer.write(frame)
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
server.socket.close()
video_capture.release()
cv2.destroyAllWindows()
