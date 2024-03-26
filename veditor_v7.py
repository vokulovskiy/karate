import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import os,sys,re

# pip install opencv-python
# pip install pillow

root = tk.Tk()
style = ttk.Style(root)
root.withdraw()
root.update()

root.attributes('-fullscreen', True)
max_width = root.winfo_screenwidth()
root.destroy()
# print("Максимальная ширина экрана:", max_width)

def read_labels(vfname, len_str=87):
    ''' Функция для чтения из файла разметки
     имя файла разметки совпадает с именем видеофайла, расширение .lbl
     Структура файла "кадр начала движения"-"кадр окончания":"метка";
     Например:
     1-20: 00000000100010000100... - строка с закодированными элементами, первые 3 символа - номер элемента
     24-36:10100000100010000100...
     Возвращает словарь вида: {1: '0000000000...', 2: '00001000100010000100...'}
     где метка присвоена каждому кадру
     len_str - длина метки, если меньше, до добавляются 0 справа, если больше, то обрезаются справа
    '''
    labels = {0:'0'*len_str}
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
                        try:
                            m=labels[i][:3]
                            for j in range(3, len_str):
                                if l[1][j]=='1' or labels[i][j]=='1':
                                    m+='1'
                                else:
                                    m+='0'
                            labels[i] = m
                        except:
                            labels[i] = l[1]
    return labels

def write_labels(vfname, labels):
    ''' Функция для записи в файл разметки
     имя файла разметки совпадает с именем видеофайла, расширение .lbl
     Структура файла "кадр начала движения"-"кадр окончания":"метка"
     Например:
     1-20: 00000000100010000100... - строка с закодированными элементами, первые 3 символа - номер элемента
     24-36:00100000100010000100...
     Аргументы:
     vfname - имя видеофайла
     labels - словарь вида {1: '0000000000...', 2: '001001000100010000100...'}
     где метка присвоена каждому кадру, если он помечен
    '''

    if len(labels) > 0:
        name = os.path.basename(vfname).split('.')[0]+'.lbl'
        lfname = os.path.join(os.path.dirname(vfname), name)
        with open(lfname, 'w') as f:
            labels = dict(sorted(labels.items())) # Сортировка по возрастанию
            len_str = len(next(iter(labels.values())))
            labels = {k: v for k, v in labels.items() if v!='0'*len_str}
            first_frame = next(iter(labels.keys()))
            last_frame = 0
            for i in labels.keys():
                if labels[i] == labels[first_frame]:
                    last_frame = i
                else:
                    if last_frame < first_frame: last_frame = first_frame
                    f.write(str(int(first_frame))+'-'+str(int(last_frame))+':'+labels[first_frame]+'\n')
                    first_frame = i
            f.write(str(int(first_frame))+'-'+str(int(last_frame))+':'+labels[first_frame]+'\n')

def read_sd(vfname):
    ''' Функция для чтения из файла справочника элементов
     имя файла на входе в функцию
     Структура файла - каждая строка наименование элемента
     1 строка - Номер оцениваемого элемента 
    '''
    if os.path.isfile(vfname):
        with open(vfname, 'r', encoding='utf-8') as f:
            lbls = [line.strip() for line in f if len(line.strip())>0]
        return lbls, len(lbls)+2 # +2 потому, что первая строка - номер элемента, 3 цифры
    
# Класс для приложения воспроизведения видео
class VideoPlayerApp:
    def __init__(self, video_source=0):
        self.window = tk.Tk()  # Создаем главное окно приложения
        self.window.after(0, self.window.deiconify)
        self.window.geometry(f'{max_width}x850')
        self.window.title(video_source)  # Устанавливаем заголовок окна
        self.str_pose = ["" for i in range(10)]  # Строки для хранения информации о времени отметок
        self.num_old = -1  # Переменная для хранения предыдущей отметки
        self.video_source = video_source  # Источник видео (0 для камеры или путь к файлу)

        # Список с расшифровками меток по умолчанию
        self.len_str = 10
        self.elements = [f'{i}:element{i}' for i in range(self.len_str)]

        self.path = os.path.dirname(self.video_source) if self.video_source else ''
        self.sd_file_path = os.path.join(self.path,'elements.txt')
        # Проверяем наличие файла с расшифровками меток и загружаем значения, если файл существует
        if os.path.isfile(self.sd_file_path):
            self.elements, self.len_str  = read_sd(self.sd_file_path) 

        # Загружаем разметку кадров
        if self.video_source and self.video_source:
            self.labels = read_labels(self.video_source, self.len_str) 

        self.vid = cv2.VideoCapture(self.video_source)  # Открываем видеопоток
        self.width = int(min(self.vid.get(cv2.CAP_PROP_FRAME_WIDTH), 1280)) 
        self.height = int(min(self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT), 720))

        # Устанавливаем размер кадра
        self.vid.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.vid.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        
        # Create frames
        self.canvas_frame = tk.Frame(self.window)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.checkbox_frame = tk.Frame(self.window)
        self.checkbox_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Создаем холст для отображения видео
        self.canvas = tk.Canvas(self.canvas_frame, width=self.width, height=self.height)
        self.canvas.pack(anchor=tk.NW)
        
        self.canvas_list = tk.Canvas(self.checkbox_frame, width=self.width, height=self.height)
        self.scrollbar = ttk.Scrollbar(self.checkbox_frame, orient=tk.VERTICAL, command=self.canvas_list.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)


        self.canvas_list.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_list.bind('<Configure>', lambda e: self.canvas_list.configure(scrollregion=self.canvas_list.bbox("all")))
        # self.canvas_list.xview_moveto(0)
        # self.canvas_list.yview_moveto(0)

        self.listbox_frame = ttk.Frame(self.canvas_list)
        self.canvas_list.create_window((0, 0), window=self.listbox_frame, anchor="nw")        
    
        # Create a Listbox
        self.listbox_active = False
        self.checkboxes = []
        self.vars = []
        self.populate_checkboxes()

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
        self.window.bind('b', self.toggle_listbox)
        self.window.bind('n', self.copy_label_f)
        self.window.bind('v', self.copy_label_r)


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

    def create_mess(self):
        frame_num = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
        txt = ''
        if frame_num in self.labels:
            txtl = [self.elements[i-2].split('|')[-1] for i,s in enumerate(self.labels[frame_num]) if s=='1' and i>2]
            txt = self.labels[frame_num][:3]+'_'+'_'.join(txtl)
            if len(self.video_label)>0:
                txt = '*' + txt
        self.message_label.config(text=txt)

    def on_scale(self, val):
        frame_num = int(float(val))
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        self.create_mess()


    # Обновление кадра видео
    def update_frame(self):
        ret, frame = self.vid.read()
        if ret:
            frame = cv2.resize(frame, (self.width, self.height))
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.scale.set(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
            if len(self.video_label)>0: # Если идет запись элемента
                self.labels[self.vid.get(cv2.CAP_PROP_POS_FRAMES)] = self.video_label
            self.update_checkboxes()

    # Обновление интерфейса
    def update(self):
        if self.window.winfo_exists():
            if self.play:
                self.update_frame()
            self.window.update_idletasks()  # Обновление интерфейса
            self.window.after(self.delay, self.update )  # Запуск обновления снова через delay миллисекунд

    # Завершение работы приложения
    def quit_app(self):
        self.window.quit()
        self.window.destroy()
        if self.video_source:
            filename = os.path.split(self.video_source)[1]
            filename = filename.split('.')[0]
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

    def copy_label_f(self, event):
        self.copy_label(1)

    def copy_label_r(self, event):
        self.copy_label(-1)

    def copy_label(self,frm):
        if self.listbox_active:
            fr = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
            self.labels[fr+frm] = self.labels[fr] 
            self.to_frame(frm-1)
                
    # Переключение воспроизведения
    def toggle_play(self, event=None):
        self.play = not self.play

    # # Отображение сообщения о текущем элементе
    # def show_message(self, num):
    #     if self.key_states[num]:
    #         self.key_states[num] = False
    #         self.message_label.config(text="")
    #         self.str_pose[num] += f'{int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))};'
    #         self.num_old = -1
    #     else:
    #         self.key_states[str(num)] = True
    #         tframes = int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))
    #         if (self.num_old != num) and (self.num_old > -1):
    #             self.str_pose[self.num_old] += f'{tframes-1};'
    #             self.key_states[str(self.num_old)] = False
    #         message = f"Element: {self.elements[str(num)]}"
    #         self.message_label.config(text=message)
    #         self.str_pose[num] += f'{tframes}-'
    #         self.num_old = num

    # Отображение окна справки
    def show_help(self):
        if not self.help_window:
            self.help_window = tk.Toplevel(self.window)
            self.help_window.title("Help")
            help_text = """Control Keys:
Space - Play/Pause
Left Arrow - Rewind 1 frame
Right Arrow - Forward 1 frame
Down Arrow - Rewind 1 second
Up Arrow - Forward 1 second
b - Edit/unEdit frame label
n - Copy label forward
v - Copy label rewind"""
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
        if file_path:
            self.window.quit()
            self.window.destroy()
            VideoPlayerApp(file_path)

    
    def toggle_listbox(self, event):
            self.listbox_active = not self.listbox_active
            if self.listbox_active:
                self.play = False
                self.update_checkboxes()
                for chb in self.checkboxes: chb.config(state=tk.NORMAL)
            else:
                self.play = False #True
                self.video_label = str(self.vars[0].get()).zfill(3)+''.join([str(self.vars[i].get()) for i in range(1,self.len_str - 2)])
                self.labels[self.vid.get(cv2.CAP_PROP_POS_FRAMES)] = self.video_label
                self.video_label = ''
                for chb in self.checkboxes: chb.config(state=tk.DISABLED)

    def populate_checkboxes(self):
        try:
            tlbl = self.labels[0]
        except:
            tlbl = '0'*self.len_str
        self.vars.append(tk.IntVar(value=int(tlbl[:3])))
        px, py = 0, 0

        def is_valid(newval):
            return re.match("^\d{1,3}$", newval) is not None

        def checkbutton_changed():
            self.labels[int(self.vid.get(cv2.CAP_PROP_POS_FRAMES))] = str(self.vars[0].get()).zfill(3)+''.join([str(self.vars[i].get()) for i in range(1,self.len_str - 2)])
            self.create_mess()

        check = (self.window.register(is_valid), "%P")
        self.checkboxes.append(ttk.Entry(self.listbox_frame,  textvariable=self.vars[0], width=3,validate="key", validatecommand=check))
        self.checkboxes[0].insert(0, tlbl[:3])
        self.checkboxes[0].grid(row=0, column=0, padx=px, pady=py, sticky="w")
        self.label1 = ttk.Label(self.listbox_frame, text = 'Номер оцениваемого элемента (0-не оценивается)')
        self.label1.grid(row=0, column=0, padx=30, pady=py, sticky="w")
        for i in range(1, self.len_str - 2):
            self.vars.append(tk.IntVar(value=int(tlbl[i+2])))
            self.checkboxes.append(ttk.Checkbutton(self.listbox_frame, 
                                        text = self.elements[i].split(';')[1], 
                                        command=checkbutton_changed,
                                        variable=self.vars[i], 
                                        onvalue=1, offvalue=0))
            self.checkboxes[i].config(state=tk.NORMAL)
            if self.elements[i].split(';')[0]=='1':
                self.checkboxes[i].grid(row=i, column=0, padx=px, pady=py, sticky="w")
        for chb in self.checkboxes: chb.config(state=tk.DISABLED)

    def update_checkboxes(self):
        try:
            tlbl = self.labels[self.vid.get(cv2.CAP_PROP_POS_FRAMES)]
        except:
            tlbl = '0'*self.len_str
        self.vars[0].set(int(tlbl[:3]))
        # self.checkboxes[0].delete(0, tk.END)
        # self.checkboxes[0].insert(0, self.vars[0])
        for i in range(1, self.len_str - 2):
            self.vars[i].set(int(tlbl[i+2]))

# Запуск приложения
if __name__ == "__main__":
    app = VideoPlayerApp()    
