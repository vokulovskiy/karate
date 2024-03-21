import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import os
from sd_format import sd  # Импорт модуля для работы с файлами конфигурации

# Пути к файлам конфигурации и разметки элементов
sd_file_path = 'config.sd'
kata_file_path = 'kata.txt'
delim = '\t'  # Разделитель для записи в файл

# Словарь с элементами по умолчанию
elements = {
    '1': 'element1', '2': 'element2', '3': 'element3', '4': 'element4', '5': 'element5', 
    '6': 'element6', '7': 'element7', '8': 'element8', '9': 'element9', '0': 'element0',
    'MAX_FRAME_WIDTH': 1280,  # Максимальная ширина кадра
    'MAX_FRAME_HEIGHT': 720    # Максимальная высота кадра
}

# Проверяем наличие файла конфигурации и загружаем значения, если файл существует
if os.path.isfile(sd_file_path):
    sd_obj = sd(sd_file_path)
    elements = sd_obj.decoding_result

# Если файл разметки элементов отсутствует, создаем его
if not os.path.isfile(kata_file_path):
    with open(kata_file_path,'w') as f:
        s='file'+delim+delim.join([elements[str(i)] for i in range(10)])
        f.write(s+'\n')

# Обновляем файл конфигурации
sd(sd_file_path, elements)

# Класс для приложения воспроизведения видео
class VideoPlayerApp:
    def __init__(self, video_source=0):
        self.window = tk.Tk()  # Создаем главное окно приложения
        self.window.title("Video Player")  # Устанавливаем заголовок окна
        self.str_pose = ["" for i in range(10)]  # Строки для хранения информации о времени отметок
        self.num_old = -1  # Переменная для хранения предыдущей отметки

        self.video_source = video_source  # Источник видео (0 для камеры или путь к файлу)

        self.vid = cv2.VideoCapture(self.video_source)  # Открываем видеопоток
        self.width = int(min(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), int(elements['MAX_FRAME_WIDTH']))) 
        self.height = int(min(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT), int(elements['MAX_FRAME_HEIGHT'])))

        # Устанавливаем размер кадра
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Создаем холст для отображения видео
        self.canvas = tk.Canvas(self.window, width=self.width, height=self.height)
        self.canvas.pack()

        # Создаем метку для вывода сообщений
        self.message_label = tk.Label(self.window, text="")
        self.message_label.pack()

        # Создаем кнопки для управления приложением
        self.btn_select_file = tk.Button(self.window, text="Select File", width=10, command=self.select_file)
        self.btn_select_file.pack(side=tk.LEFT)

        self.btn_play = tk.Button(self.window, text="Play", width=10, command=self.play_video)
        self.btn_play.pack(side=tk.LEFT)

        self.btn_stop = tk.Button(self.window, text="Stop", width=10, command=self.stop_video)
        self.btn_stop.pack(side=tk.LEFT)

        self.btn_help = tk.Button(self.window, text="Help", width=10, command=self.show_help)
        self.btn_help.pack(side=tk.LEFT)

        self.btn_quit = tk.Button(self.window, text="Quit", width=10, command=self.quit_app)
        self.btn_quit.pack(side=tk.LEFT)

        # Создаем шкалу для перемотки видео
        self.scale = tk.Scale(self.window, from_=0, to=self.vid.get(cv2.CAP_PROP_FRAME_COUNT), 
                              orient=tk.HORIZONTAL, command=self.on_scale)
        self.scale.pack(fill=tk.X)

        self.delay = 10  # Задержка между кадрами (миллисекунды)
        self.play = False  # Флаг воспроизведения видео
        if video_source:
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, 1)  # Устанавливаем начальный кадр
        self.update_frame()  # Обновляем кадр
        self.update()  # Обновляем интерфейс

        self.window.protocol("WM_DELETE_WINDOW", self.quit_app)  # Действие при закрытии окна

        # Привязываем клавиши к методам управления
        self.window.bind('<Left>', self.backward_one_frame)
        self.window.bind('<Right>', self.forward_one_frame)
        self.window.bind('<space>', self.toggle_play)
        self.window.bind('<Down>', self.backward_one_second)
        self.window.bind('<Up>', self.forward_one_second)
        self.key_states = {str(i): False for i in range(10)}  # Состояния клавиш 0-9
        for i in range(10):
            self.window.bind(str(i), lambda event, num=i: self.show_message(num))  # Привязываем клавиши к методу отметки времени

        self.help_window = None  # Окно справки
        self.window.focus_set()  # Устанавливаем фокус на главное окно
              
        self.window.mainloop()  # Запускаем главный цикл приложения

    # Методы для управления воспроизведением видео
    def play_video(self):
        if not self.vid.isOpened():
            self.vid = cv2.VideoCapture(self.video_source)
        self.play = True

    def stop_video(self):
        self.play = False

    def on_scale(self, val):
        frame_num = int(float(val))
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_num)

    # Обновление кадра видео
    def update_frame(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.resize(frame, (self.width, self.height))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    # Обновление интерфейса
    def update(self):
        if self.window.winfo_exists():
            if self.play:
                self.update_frame()
                self.scale.set(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
            self.window.update_idletasks()  # Обновление интерфейса
            self.window.after(self.delay, self.update )  # Запуск обновления снова через delay миллисекунд

    # Завершение работы приложения
    def quit_app(self):
        self.window.quit()
        self.window.destroy()
        _, filename = os.path.split(self.video_source)
        filename = filename.split('.')[0]
        s = delim.join([self.str_pose[i] for i in range(10)])  # Строка для записи в файл
        with open(kata_file_path,'a') as f:
            f.write(f'{filename}{delim}{s}\n')  # Записываем данные в файл
    
    # Методы для перемотки видео и отметки времени
    def to_frame(self,fr=0):
        current_frame = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, current_frame + fr)
        self.update_frame()
        self.scale.set(self.vid.get(cv2.CAP_PROP_POS_FRAMES))

    def forward_one_frame(self, event):
        self.to_frame(0)

    def backward_one_frame(self, event):
        self.to_frame(-2)

    def forward_one_second(self, event):
        self.to_frame(30)

    def backward_one_second(self, event):
        self.to_frame(-30)

    # Переключение воспроизведения
    def toggle_play(self, event=None):
        self.play = not self.play

    # Отображение сообщения о текущем элементе
    def show_message(self, num):
        if self.key_states[str(num)]:
            self.key_states[str(num)] = False
            self.message_label.config(text="")
            self.str_pose[num] += f'{int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))};'
            self.num_old = -1
        else:
            self.key_states[str(num)] = True
            tframes = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
            if (self.num_old != num) and (self.num_old > -1):
                self.str_pose[self.num_old] += f'{tframes-1};'
                self.key_states[str(self.num_old)] = False
            message = f"Element: {elements[str(num)]}"
            self.message_label.config(text=message)
            self.str_pose[num] += f'{tframes}-'
            self.num_old = num

    # Отображение окна справки
    def show_help(self):
        if not self.help_window:
            self.help_window = tk.Toplevel(self.window)
            self.help_window.title("Help")
            s = '\n'.join([f'{i} : {elements[str(i)]}' for i in range(10)])
            help_text = """Control Keys:
Space - Play/Pause
Left Arrow - Rewind 1 frame
Right Arrow - Forward 1 frame
Down Arrow - Rewind 1 second
Up Arrow - Forward 1 second
0-9 - Start/Stop marking the element\n"""+s
            help_label = tk.Label(self.help_window, text=help_text)
            help_label.pack()

            self.help_window.protocol("WM_DELETE_WINDOW", self.close_help_window)

    # Закрытие окна справки
    def close_help_window(self):
        self.help_window.destroy()
        self.help_window = None

    # Выбор файла видео
    def select_file(self):
        file_path = filedialog.askopenfilename()
        print(file_path)
        if file_path:
            self.window.quit()
            self.window.destroy()
            VideoPlayerApp(file_path)

# Запуск приложения
if __name__ == "__main__":
    app = VideoPlayerApp()    
