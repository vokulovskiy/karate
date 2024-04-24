import cv2
import mediapipe as mp
import json
import os

# Инициализация MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def pose2json(vfile):
    # Загрузка видеофайла
    cap = cv2.VideoCapture(vfile)

    # Получить имя видеофайла без расширения
    video_name = vfile.split('.')[0]

    # Список для хранения координат ключевых точек для каждого кадра
    pose_landmarks_per_frame = []

    frame_count = 0
    while True:
        success, img = cap.read()
        if not success:
            break

        # Детекция позы
        results = pose.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        # Извлечение координат ключевых точек
        json_dict = {
            'frame': frame_count,
            'people': [{
                'person_id': [-1],
                'pose_keypoints_2d': [],
                'pose_keypoints_3d': []
            }]
        }

        # Process 2D pose landmarks
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                json_dict['people'][0]['pose_keypoints_2d'].append({
                    'x': landmark.x, 
                    'y': landmark.y, 
                    'z': landmark.z, 
                    'visibility': landmark.visibility
                })

        # Process 3D pose world landmarks
        if results.pose_world_landmarks:
            for landmark in results.pose_world_landmarks.landmark:
                json_dict['people'][0]['pose_keypoints_3d'].append({
                    'x': landmark.x, 
                    'y': landmark.y, 
                    'z': landmark.z, 
                    'visibility': landmark.visibility
                })

        if results.pose_landmarks:
            pose_landmarks_per_frame.append(json_dict)

        # Отрисовка ключевых точек (опционально)
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing.draw_landmarks(img, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        cv2.imshow('Image', img)
        if cv2.waitKey(1) == ord('q'):
            break

        # if frame_count >100:
        #     break

        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()

    # Сохранение координат ключевых точек в JSON-файл
    json_file_name = f"{video_name}.json"
    with open(json_file_name, 'w') as json_file:
        json.dump(pose_landmarks_per_frame, json_file, indent=2)

dirs = [r'C:\temp\Cam_1_1920x1080x60']
files = []
cnt=0
for d in dirs:
    for f in os.listdir(d):
        ext=os.path.splitext(f)[1].lower()
        if ext in ['.mp4','.avi','.mov','.mts']:
            files.append(os.path.join(d,f))
            pose2json(files[-1])
            cnt+=1
            print(f"{cnt}/{80}  Обработан файл: {files[-1]}")