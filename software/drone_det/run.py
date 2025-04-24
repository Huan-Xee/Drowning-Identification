import cv2
import torch
from tracker import *
import numpy as np
import mediapipe as mp
import playsound
from mutagen.mp3 import MP3
import time
import miniaudio

mpPose = mp.solutions.pose
pose = mpPose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
mpDraw = mp.solutions.drawing_utils

ALARM_PATH = "accident.mp3"
# model = torch.hub.load('ultralytics/yolov5', 'custom', path='best.pt', force_reload=True)
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

cap = cv2.VideoCapture('3.mp4')

tracker = Tracker()
c = set()


def calc_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


file = 'assets_alarm.mp3'
audio = MP3(file)
length = audio.info.length

frame_check = 7
flag = 0
while True:
    ret, frame = cap.read()
    if ret == False:
        break
    # frame=cv2.resize(frame,(1020,500))
    results = model(frame)
    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Apply the mediapipe pose detection module for detection
    result = pose.process(imgRGB)
    # print(results.pose_landmarks)
    h, w, c = frame.shape
    # Draw landmarks
    if result.pose_landmarks:
        mpDraw.draw_landmarks(frame, result.pose_landmarks, mpPose.POSE_CONNECTIONS)
        landmarks = result.pose_landmarks.landmark

        # for land in mpPose.PoseLandmark:
        # print(land)
        l_shoulder = [landmarks[mpPose.PoseLandmark.LEFT_SHOULDER.value].x,
                      landmarks[mpPose.PoseLandmark.LEFT_SHOULDER.value].y]
        l_elbow = [landmarks[mpPose.PoseLandmark.LEFT_ELBOW.value].x,
                   landmarks[mpPose.PoseLandmark.LEFT_ELBOW.value].y]
        l_wrist = [landmarks[mpPose.PoseLandmark.LEFT_WRIST.value].x,
                   landmarks[mpPose.PoseLandmark.LEFT_WRIST.value].y]

        r_shoulder = [landmarks[mpPose.PoseLandmark.RIGHT_SHOULDER.value].x,
                      landmarks[mpPose.PoseLandmark.RIGHT_SHOULDER.value].y]
        r_elbow = [landmarks[mpPose.PoseLandmark.RIGHT_ELBOW.value].x,
                   landmarks[mpPose.PoseLandmark.RIGHT_ELBOW.value].y]
        r_wrist = [landmarks[mpPose.PoseLandmark.RIGHT_WRIST.value].x,
                   landmarks[mpPose.PoseLandmark.RIGHT_WRIST.value].y]

        l_ang = calc_angle(l_shoulder, l_elbow, l_wrist)
        r_ang = calc_angle(r_shoulder, r_elbow, r_wrist)

        cv2.putText(frame, str(int(l_ang)), tuple(np.multiply(l_elbow, [640, 480]).astype(int)),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 1)
        cv2.putText(frame, str(int(r_ang)), tuple(np.multiply(r_elbow, [640, 480]).astype(int)),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 1)

        if l_wrist[1] * h < l_elbow[1] * h < l_shoulder[1] * h and l_ang > 150:

            flag += 1
            if flag >= frame_check:
                cv2.putText(frame, 'Warnning!!! someone need help', (20, 75), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                stream = miniaudio.stream_file(file)
                with miniaudio.PlaybackDevice() as device:
                    device.start(stream)
                    time.sleep(length)

        elif r_wrist[1] * h < r_elbow[1] * h < r_shoulder[1] * h and r_ang > 150:

            flag += 1
            if flag >= frame_check:
                cv2.putText(frame, 'Warnning!!! someone need help', (20, 75), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
                stream = miniaudio.stream_file(file)
                with miniaudio.PlaybackDevice() as device:
                    device.start(stream)
                    time.sleep(length)

    points = []
    for index, row in results.pandas().xyxy[0].iterrows():

        x1 = int(row['xmin'])
        y1 = int(row['ymin'])
        x2 = int(row['xmax'])
        y2 = int(row['ymax'])
        n = (row['name'])

        if 'person' in n:
            if row['confidence'] > 0.25:
                points.append([x1, y1, x2, y2])
                # cv2.rectangle(frame,(x1,y1),(x2,y2),(255,0,255),2)
            # cv2.putText(frame,str(n),(x1,y1),cv2.FONT_HERSHEY_PLAIN,2,(255,0,255),2)
    boxes_id = tracker.update(points)
    num = len(points)
    id = []
    # person_id = []
    for box_id in boxes_id:
        x, y, w, h, idd = box_id
        id.append(idd)

        cv2.rectangle(frame, (x, y), (w, h), (0, 255, 0), 2)
        cv2.putText(frame, 'number of persons is=' + str(num), (20, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 3)
        cv2.putText(frame, 'person ID is=' + str(id[-1]), (x, y), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)

    cv2.imshow('FRAME', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()