import tkinter as tk
from tkinter import Tk, RIGHT, BOTH, RAISED, LEFT
from tkinter.ttk import Frame, Button, Style
 
 
def main():
 
    # root = Tk()
    # root.geometry("300x200+300+300")
    # frame1 = Frame(root)
    # frame2 = Frame(frame1, relief=RAISED, borderwidth=1)
    # frame2.pack(fill=BOTH, expand=True)

    # frame1.pack(fill=BOTH, expand=True)

    # closeButton = Button(frame1, text="Закрыть")
    # closeButton.pack(side=RIGHT, padx=5, pady=5)
    # okButton = Button(frame1, text="Готово")
    # okButton.pack(side=RIGHT)
    root = tk.Tk()
    root.geometry("600x400+300+300")
    root.title("Multi-Video Player")
    # Создаем фрейм для кнопок
    button_frame = tk.Frame(root)

    # Создаем фрейм для видео
    v_frame = tk.Frame(button_frame, relief=RAISED, borderwidth=1)
    v_frame.pack(fill=BOTH, expand=True)
    button_frame.pack(fill=BOTH, expand=True)

     # Создаем кнопку Play/Pause
    play_pause_button = tk.Button(button_frame, text="Воспроизвести/Пауза") #, command=lambda: [player.play_pause() for player in players])
    # Создаем кнопку Исполнитель
    ex_button = tk.Button(button_frame, text="Исполнитель")#, command=select_ex)
    # Создаем метку для вывода сообщений
    message_label = tk.Label(button_frame, text="Message")
    play_pause_button.pack(side=LEFT, padx=5, pady=5)
    ex_button.pack(side=LEFT, padx=5, pady=5)
    message_label.pack(side=LEFT, padx=5, pady=5)
    root.mainloop()
 
 
if __name__ == '__main__':
    main()