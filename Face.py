import cv2
import face_recognition
import sqlite3
from datetime import datetime

# Connect to SQLite database
conn = sqlite3.connect('school_attendance.db')
c = conn.cursor()

# Create table to store student information
c.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY, name TEXT, face_encoding TEXT)''')

# Create table to store attendance records
c.execute('''CREATE TABLE IF NOT EXISTS attendance
             (id INTEGER PRIMARY KEY, student_id INTEGER, timestamp DATETIME)''')

# Function to add student to the database
def add_student(name, face_encoding):
    c.execute("INSERT INTO students (name, face_encoding) VALUES (?, ?)", (name, face_encoding))
    conn.commit()

# Function to mark attendance
def mark_attendance(student_id):
    timestamp = datetime.now()
    c.execute("INSERT INTO attendance (student_id, timestamp) VALUES (?, ?)", (student_id, timestamp))
    conn.commit()

# Function to recognize faces and mark attendance
def recognize_faces(frame):
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encodings:
        # Compare face encoding with known faces in the database
        c.execute("SELECT id, face_encoding FROM students")
        rows = c.fetchall()
        for row in rows:
            known_face_encoding = eval(row[1])
            matches = face_recognition.compare_faces([known_face_encoding], face_encoding)
            if True in matches:
                student_id = row[0]
                mark_attendance(student_id)
                # Draw rectangle and label on recognized face
                top, right, bottom, left = face_recognition.face_locations(rgb_frame)[0]
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, 'Student ID: ' + str(student_id), (left + 6, bottom - 6),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                break

# Capture video from camera
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    recognize_faces(frame)
    cv2.imshow('Video', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
