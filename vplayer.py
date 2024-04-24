import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd

def process_frames(frames): 
    text_output = "Frame data: "
    for frame in frames:
        text_output += f"{frame.shape}, "
    return text_output

def video_player(files,frames):
    class VideoPlayer:
        def __init__(self, master, video_path, frame_num):
            self.master = master
            self.cap = cv2.VideoCapture(video_path)
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            self.frame = None
            self.paused = True
            self.frame_w = 0 # признак обновления кадра
            self.width = fwidth
            self.height = fheight 
            # Устанавливаем размер кадра
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

            # Создаем фрейм для видео и элементов управления
            self.video_frame = tk.Frame(master, width=self.width, height=self.height)
            self.video_frame.grid(row=0, column=0)

            # Создаем холст для отображения видео
            self.canvas = tk.Canvas(self.video_frame, width=self.width, height=self.height)
            self.canvas.grid(row=1, column=0)

            # Создаем поле для ввода номера кадра
            self.time_entry = tk.Entry(self.video_frame)
            self.time_entry.grid(row=2, column=0)
            
            self.master.protocol("WM_DELETE_WINDOW", self.quit_app)  # Действие при закрытии окна

            # Обновляем кадр видео
            self.update_frame()

        def update_frame(self):
            if not self.paused and self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.frame_w = 1 # признак обновления кадра
                    # Конвертируем кадр в формат, совместимый с Tkinter
                    self.frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    # Изменяем размер кадра перед конвертацией
                    resized_frame = cv2.resize(self.frame, (self.width, self.height))  # Изменяем размер 
                    self.photo = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
                    self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

                    # Обновляем номер кадра воспроизведения
                    self.time_entry.delete(0, tk.END)
                    self.time_entry.insert(0, self.cap.get(cv2.CAP_PROP_POS_FRAMES))

                    proc = sum([player.frame_w for player in players]) # проверяем, что кадры во всех плеерах обновились
                    if proc == len(players): # кадры во всех плеерах обновились
                        frames = [player.frame for player in players]
                        text_output = process_frames(frames)
                        # Обновляем метку message_label с выводом текста
                        message_label.config(text=text_output)
                        for player in players: # проверяем, что кадры во всех плеерах обновились
                            player.frame_w = 0

            self.master.update_idletasks()  # Обновление интерфейса
            # Планируем следующий вызов update_frame через 1 мс
            self.master.after(1, self.update_frame)

        def play_pause(self):
            self.paused = not self.paused
        # Завершение работы приложения
        def quit_app(self):
            self.master.quit()
            self.master.destroy()

    def select_ex():
        root.quit()
        root.destroy()
        select_executor()

    # Создаем главное окно
    root = tk.Tk()
    root.title("Multi-Video Player")
    root.attributes('-fullscreen', True)
    max_width = root.winfo_screenwidth()
    max_height = root.winfo_screenheight()
    root.geometry(f"{max_width-max_width//10}x{max_height}+0+0")
    root.attributes('-fullscreen', False)
    nplayers = len(files)
    # Создаем фрейм для кнопок
    button_frame = tk.Frame(root)
     # Создаем кнопку Play/Pause
    play_pause_button = tk.Button(button_frame, text="Воспроизвести/Пауза", command=lambda: [player.play_pause() for player in players])
    # Создаем кнопку Исполнитель
    ex_button = tk.Button(button_frame, text="Исполнитель", command=select_ex)
    # Создаем метку для вывода сообщений
    message_label = tk.Label(button_frame, text="Message")
    
    
    rasp = [[0,0],[0,1],[1,0],[1,1]]
    if nplayers == 1:
        fwidth=max_width - max_width//9
        fheight=max_height - max_height//9
        button_frame.grid(row=1)
        play_pause_button.grid(row=0, column=0)
        ex_button.grid(row=0, column=1)
        message_label.grid(row=0, column=2)
        players = [VideoPlayer(root, files[0], frames[0])]
        players[0].video_frame.grid(row=0, column=0)
    else:
        fwidth=max_width//2 - max_width//15
        fheight=max_height//2 - max_height//15
        button_frame.grid(row=2)
        play_pause_button.grid(row=0, column=0)
        ex_button.grid(row=0, column=1)
        message_label.grid(row=0, column=2)
        # Создаем видеоплееры
        players = [VideoPlayer(root, file, frames[i]) for i,file in enumerate(files)]
        # Размещаем видеоплееры в шахматном порядке
        for i in range(nplayers):
            players[i].video_frame.grid(row=rasp[i][0], column=rasp[i][1])

    for i in range(nplayers):
            players[i].paused = False
    # Запускаем главный цикл Tkinter
    root.mainloop()
    
def select_executor():
    dirs = [r'C:/temp/Cam_1_1920x1080x60/', r'C:/temp/Cam_2_1920x1080x60/', r'C:/temp/Cam_3_1920x1080x60/', r'C:/temp/Cam_4_1920x1080x60/']
    df = pd.read_excel(r'C:\Users\user\Documents\python\karate\video_base_index.xlsx')
    executors = df['Название'].to_list()


    # Создаем главное окно
    root1 = tk.Tk()
    root1.title("Выбор исполнителя")
    root1.overrideredirect(True)  # Убираем границы окна
    #root1.geometry("300x50")  # Устанавливаем ширину окна 

    # Функция для обработки выбранного значения
    def get_selected_executor(event):
        selected_executor = executor_combobox.get()
        root1.quit()  # Закрываем окно после выбора
        root1.destroy()
        i = executors.index(selected_executor)
        files = [dirs[j]+df.loc[i,[f'Камера_{j+1}']].values[0] for j in range(4)]
        frames = [df.loc[i,[f'df{j+1}']].values[0] for j in range(4)]
        video_player(files,frames)

    # Создаем комбобокс (выпадающий список)
    executor_combobox = ttk.Combobox(root1, values=executors, width=30)
    executor_combobox.current(0)  # Устанавливаем первый элемент по умолчанию
    executor_combobox.pack(pady=20)

    # Устанавливаем обработчик события для выбора значения
    executor_combobox.bind("<<ComboboxSelected>>", get_selected_executor)

    # Запускаем главный цикл
    root1.mainloop()

select_executor()