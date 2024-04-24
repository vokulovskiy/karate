import csv
import cv2
import mediapipe as mp

def extract_pose_landmarks(video_file, model_complexity=1, landmarks_to_use=None):
  """
  Извлекает ключевые точки позы с помощью Mediapipe для каждого кадра видеофайла 
  и сохраняет их в мировых координатах вместе с номером кадра и временем в файл CSV.

  Args:
      video_file: Имя видеофайла.
      model_complexity: Сложность модели Pose Landmark (0, 1 или 2).
      landmarks_to_use: Список индексов ключевых точек, которые нужно извлечь.
  """
  mp_drawing = mp.solutions.drawing_utils
  mp_pose = mp.solutions.pose

  # Получить имя csv
  csv_name = video_file.split('.')[0]+'.csv'

  with mp_pose.Pose(
      model_complexity=model_complexity,
      static_image_mode=False, min_detection_confidence=0.5) as pose, \
       open(csv_name, 'w', newline='') as csvfile:

    writer = csv.writer(csvfile, delimiter=';')
    row = ['Frame', 'Time (ms)']
    landmarks_to_use = [i for i in range(33)] if landmarks_to_use is None else landmarks_to_use
    for i in landmarks_to_use:
        s = str(i)
        row.extend(['X'+s,'Y'+s,'Z'+s,'V'+s])

    writer.writerow(row)
    cap = cv2.VideoCapture(video_file)

    frame_idx = 0
    while cap.isOpened():
      success, image = cap.read()
      if not success:
        print("Ignoring empty camera frame.")
        break

      # Переводим изображение из BGR в RGB
      image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

      # Делаем изображение неизменяемым для повышения производительности
      image.flags.writeable = False
      
      # Получаем результаты
      results = pose.process(image)

      # Делаем изображение изменяемым
      image.flags.writeable = True
      
      # Переводим изображение обратно в BGR
      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

      # Извлекаем ключевые точки в мировых координатах
      if results.pose_world_landmarks:

        # Получаем время кадра в миллисекундах
        frame_time_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

        # Собираем данные для строки
        row_data = []
        for landmark_idx, landmark in enumerate(results.pose_world_landmarks.landmark):
            if landmarks_to_use is None or landmark_idx in landmarks_to_use:
                row_data.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])

        # Записываем строку с номером кадра, временем и данными ключевых точек
        writer.writerow([frame_idx, round(frame_time_ms)] + row_data)

      # Рисуем скелет на изображении (опционально)
      mp_drawing.draw_landmarks(
          image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
      cv2.imshow('Image', image)
      if cv2.waitKey(1) == ord('q'):
            break

      frame_idx += 1

    cap.release()

kd = [0,11,12,13,14,15,16,23,24,25,26,27,28,29,30,31,32]
extract_pose_landmarks(r"C:\temp\Cam_1_1920x1080x60\20240209_181457.mp4",1,kd)