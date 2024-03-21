import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
import os

root = tk.Tk()
root.attributes('-fullscreen', True)
max_width = root.winfo_screenwidth()
root.attributes('-fullscreen', False)
root.destroy()
# print("Максимальная ширина экрана:", max_width)

delim = '\t'  # Разделитель для записи в файл

def read_labels(vfname):
    ''' Функция для чтения из файла разметки
     имя файла разметки совпадает с именем видеофайла, расширение .lbl
     Структура файла "кадр начала движения"-"кадр окончания":"метка";
     Например:
     1-20:CH1_S_DZKD_MVLFT
     24-36:СН2_A_SWNG_BLK
     Возвращает словарь вида: {1: 'CH1_S_DZKD_MVLFT', 2: 'CH1_S_DZKD_MVLFT',3: 'CH1_S_DZKD_MVLFT',  24: 'СН2_A_SWNG_BLK'}
     где метка присвоена каждому кадру, если он помечен
    '''
    labels = {}
    name = os.path.basename(vfname).split('.')[0]+'.lbl'
    lfname = os.path.join(os.path.dirname(vfname), name)
    if os.path.isfile(lfname):
        with open(lfname, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    l = line.split(':')
                    l1 = l[0].split('-')
                    for i in range(int(l1[0]), int(l1[1])+1):
                        labels[i] = l[1]
                        print(i, labels[i])
        return labels

def write_labels(vfname, labels):
    ''' Функция для записи в файл разметки
     имя файла разметки совпадает с именем видеофайла, расширение .lbl
     Структура файла "кадр начала движения"-"кадр окончания":"метка"
     Например:
     1-20:CH1_S_DZKD_MVLFT
     24-36:СН2_A_SWNG_BLK
     Аргументы:
     vfname - имя видеофайла
     labels - словарь вида {1: 'CH1_S_DZKD_MVLFT', 2: 'CH1_S_DZKD_MVLFT',3: 'CH1_S_DZKD_MVLFT',  24: 'СН2_A_SWNG_BLK'}
     где метка присвоена каждому кадру, если он помечен
    '''

    if len(labels) > 0:
        name = os.path.basename(vfname).split('.')[0]+'.lbl'
        lfname = os.path.join(os.path.dirname(vfname), name)
        with open(lfname, 'w') as f:
            labels = dict(sorted(labels.items())) # Сортировка по возрастанию
            first_frame = next(iter(labels.keys()))
            last_frame = 0
            for i in sorted(labels.keys()):
                if labels[i] == labels[first_frame]:
                    last_frame = i
                else:
                    f.write(str(int(first_frame))+'-'+str(int(last_frame))+':'+labels[first_frame]+'\n')
                    first_frame = i
            f.write(str(first_frame)+'-'+str(last_frame)+':'+labels[first_frame]+'\n')

def read_sd(vfname):
    ''' Функция для чтения из файла справочника элементов
     имя файла на входе в функцию
     Структура файла "метка" = "расшифровка"
     Например:
     CH1_S_DZKD_MVLFT = Движение влево в "Дзэнкуцу-дачи"
     CH2_A_SWNG_BLK = Подготовка к выполнению блока (замах) "Гедан Барай"
     Возвращает словарь вида: {'CH1_S_DZKD_MVLFT':'Движение влево в "Дзэнкуцу-дачи"', 'CH2_A_SWNG_BLK': 'Подготовка к выполнению блока (замах) "Гедан Барай"'}
    '''
    labels = {}
    if os.path.isfile(vfname):
        with open(vfname, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    l = line.split('=')
                    labels[l[0].strip()] = l[1].strip()
        return labels
    
# Класс для приложения воспроизведения видео
class VideoPlayerApp:
    def __init__(self, video_source=0):
        self.window = tk.Tk()  # Создаем главное окно приложения
        self.window.geometry(f'{max_width}x850')
        self.window.title(video_source)  # Устанавливаем заголовок окна
        self.str_pose = ["" for i in range(10)]  # Строки для хранения информации о времени отметок
        self.num_old = -1  # Переменная для хранения предыдущей отметки
        self.video_source = video_source  # Источник видео (0 для камеры или путь к файлу)

        if self.video_source:
            self.path = os.path.dirname(self.video_source) # Пути к файлам конфигурации и разметки элементов
            self.labels = read_labels(self.video_source)
        else:
            self.path = ''
            self.labels = {}
        self.sd_file_path = os.path.join(self.path,'config.sd')
        print(self.labels)

        # Словарь с элементами по умолчанию
        self.state_keys = [str(i) for i in range(10)]
        self.elements = {i:'element'+str(i) for i in self.state_keys}


        # Проверяем наличие файла конфигурации и загружаем значения, если файл существует
        if os.path.isfile(self.sd_file_path):
            self.elements = read_sd(self.sd_file_path)
            self.state_keys = [i for i in self.elements.keys()]
      
        self.vid = cv2.VideoCapture(self.video_source)  # Открываем видеопоток
        self.width = int(min(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), 1280)) 
        self.height = int(min(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT), 720))

        # Устанавливаем размер кадра
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Create frames
        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.listbox_frame = tk.Frame(self.window)
        self.listbox_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create a Listbox
        self.listbox = tk.Listbox(self.listbox_frame, selectmode=tk.SINGLE, width=max_width-self.width, height=self.height)
        self.listbox_active = False
        self.listbox.pack(side=tk.RIGHT, fill=tk.Y)
        #self.listbox.insert(tk.END, *self.state_keys)
        self.populate_listbox()
        self.listbox.config(state=tk.DISABLED)
        
        # Создаем холст для отображения видео
        self.canvas = tk.Canvas(self.canvas_frame, width=self.width, height=self.height)
        self.canvas.pack(anchor=tk.NW)

        # Создаем метку для вывода сообщений
        self.message_label = tk.Label(self.canvas_frame, text="")
        self.message_label.pack(fill=tk.X)

        # Создаем шкалу для перемотки видео
        self.scale = tk.Scale(self.canvas_frame, from_=0, to=self.vid.get(cv2.CAP_PROP_FRAME_COUNT), 
                              orient=tk.HORIZONTAL, command=self.on_scale)
        self.scale.pack(fill=tk.X)

        # Создаем кнопки для управления приложением
        self.btn_select_file = tk.Button(self.canvas_frame, text="Select File", width=10, command=self.select_file)
        self.btn_select_file.pack(side=tk.LEFT)

        self.btn_play = tk.Button(self.canvas_frame, text="Play", width=10, command=self.play_video)
        self.btn_play.pack(side=tk.LEFT)

        self.btn_stop = tk.Button(self.canvas_frame, text="Stop", width=10, command=self.stop_video)
        self.btn_stop.pack(side=tk.LEFT)

        self.btn_help = tk.Button(self.canvas_frame, text="Help", width=10, command=self.show_help)
        self.btn_help.pack(side=tk.LEFT)

        self.btn_quit = tk.Button(self.canvas_frame, text="Quit", width=10, command=self.quit_app)
        self.btn_quit.pack(side=tk.LEFT)

        self.delay = 1  # Задержка между кадрами (миллисекунды)
        self.play = False  # Флаг воспроизведения видео
        self.video_label = "" # метка записываемого элемента
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
        self.window.bind('<b>', self.toggle_listbox)
        self.window.bind('<n>', self.clear_message_label)

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
        txt = ''
        if frame_num in self.labels:
            txt = f'{self.labels[frame_num]}:{self.elements[self.labels[frame_num]]}'
            if len(self.video_label)>0:
                txt = '*' + txt
        self.message_label.config(text=txt)
        

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
                if len(self.video_label)>0: # Если идет запись элемента
                    self.labels[self.vid.get(cv2.CAP_PROP_POS_FRAMES)] = self.video_label
            self.window.update_idletasks()  # Обновление интерфейса
            self.window.after(self.delay, self.update )  # Запуск обновления снова через delay миллисекунд

    # Завершение работы приложения
    def quit_app(self):
        self.window.quit()
        self.window.destroy()
        if self.video_source:
            filename = os.path.split(self.video_source)[1]
            filename = filename.split('.')[0]
            s = delim.join([self.str_pose[i] for i in range(10)])  # Строка для записи в файл
            write_labels(self.video_source, self.labels)
    
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
        if self.key_states[num]:
            self.key_states[num] = False
            self.message_label.config(text="")
            self.str_pose[num] += f'{int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))};'
            self.num_old = -1
        else:
            self.key_states[str(num)] = True
            tframes = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
            if (self.num_old != num) and (self.num_old > -1):
                self.str_pose[self.num_old] += f'{tframes-1};'
                self.key_states[str(self.num_old)] = False
            message = f"Element: {self.elements[str(num)]}"
            self.message_label.config(text=message)
            self.str_pose[num] += f'{tframes}-'
            self.num_old = num

    # Отображение окна справки
    def show_help(self):
        if not self.help_window:
            self.help_window = tk.Toplevel(self.window)
            self.help_window.title("Help")
            s = '\n'.join([f'{i} : {self.elements[str(i)]}' for i in range(10)])
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

    
    def toggle_listbox(self, event):
#         if event.char == "b":
            self.listbox_active = not self.listbox_active
            if self.listbox_active:
                self.play = False
                self.listbox.config(state=tk.NORMAL)
            else:
                selected_indices = self.listbox.curselection()
                self.play = True
                if selected_indices:
                    selected_index = selected_indices[0]
                    selected_value = self.listbox.get(selected_index)
                    self.video_label = selected_value.split(':')[0]
                    self.message_label.config(text='* ' + self.elements[self.video_label])
                    self.labels[self.vid.get(cv2.CAP_PROP_POS_FRAMES)] = self.video_label
                self.listbox.config(state=tk.DISABLED)

    def populate_listbox(self):
        for i,element in self.elements.items():
            self.listbox.insert(tk.END, i+':'+element)

    def clear_message_label(self, event):
        self.video_label = ''
        frame_num = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
        if frame_num in self.labels:
            self.message_label.config(text=self.labels[frame_num])
        else:
            self.message_label.config(text='')   


# Запуск приложения
if __name__ == "__main__":
    app = VideoPlayerApp()    
