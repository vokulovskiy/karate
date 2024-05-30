import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.animation as animation
from sklearn.preprocessing import MinMaxScaler
import sys

points = {
    0:'nose',
    2:'left_eye',
    5:'right_eye',
    11:'left_shoulder',
    12:'right_shoulder',
    13:'left_elbow',
    14:'right_elbow',
    15:'left_wrist',
    16:'right_wrist',
    17:'left_pinky',
    18:'right_pinky',
    19:'left_index',
    20:'right_index',
    21:'left_thumb',
    22:'right_thumb',
    23:'left_hip',
    24:'right_hip',
    25:'left_knee',
    26:'right_knee',
    27:'left_ankle',
    28:'right_ankle',
    29:'left_heel',
    30:'right_heel',
    31:'left_foot_index',
    32:'right_foot_index',
    }
lines = [
    [0,2],
    [0,5],
    [14,16],
    [12,14],
    [12,11],
    [11,13],
    [13,15],
    [12,24],
    [11,23],
    [23,24],
    [24,26],
    [23,25],
    [26,28],
    [25,27],
    [28,32],
    [28,30],
    [30,32],
    [27,29],
    [27,31],
    [29,31]
    ]
new_col = [
    'ExecutionNumber','KataInfo','KataNumber','AthleteNumber','Frame','N_ELEM','S','A','STR','BLK','REY','HKD','FUD','UHD','DZKD','KOKD','NKSD','UPP',
    'MDL','LOW','SIML','L','R','HND','UPA','SD','CRCL','OUTS','DW','SWNG','MVFRW','MVBCK','MVLFT','MVRHT','ROT45','ROT180','FSTF','FSTHMR','HNDKNF',
    'ERRD','ERRM','ERRS','ERRB','Time','X_24','Y_24','Z_24','X_26','Y_26','Z_26','X_28','Y_28','Z_28','X_30','Y_30','Z_30','X_32','Y_32','Z_32',
    'X_23','Y_23','Z_23','X_25','Y_25','Z_25','X_27','Y_27','Z_27','X_29','Y_29','Z_29','X_31','Y_31','Z_31','X_0','Y_0','Z_0','X_5','Y_5','Z_5',
    'X_2','Y_2','Z_2','X_12','Y_12','Z_12','X_14','Y_14','Z_14','X_16','Y_16','Z_16','X_18','Y_18','Z_18','X_20','Y_20','Z_20','X_22','Y_22','Z_22',
    'X_11','Y_11','Z_11','X_13','Y_13','Z_13','X_15','Y_15','Z_15','X_17','Y_17','Z_17','X_19','Y_19','Z_19','X_21','Y_21','Z_21'
    ]
cam = 1
nfile = 0
if cam==1:
    fn1 = [
        r"C:\temp\Cam_1_1920x1080x60\20240209_181457.csv",
        r"C:\temp\Cam_2_1920x1080x60\IMG_3468.csv",
        r"C:\temp\Cam_3_1920x1080x60\20240209_181458.csv",
        r"C:\temp\Cam_4_1920x1080x60\Тайкёку соно ити 1.csv",
        r"DS\train_base.csv"
    ]
    data = pd.read_csv(fn1[nfile],delimiter=';')
else:
    fn1=[
        r'DS\DATASET\YX_DS01.csv',
        r'DS\DATASET\YX_DS02.csv',
        r'DS\DATASET\YX_DS03.csv',
        r'DS\DATASET\YX_DS04.csv',
        r'DS\DATASET\YX_DS05.csv'
        ]
    data = pd.read_csv(fn1[nfile])
    data.columns = new_col
    # # Вычисляем среднюю точку между бедрами
    center_x = (data['X_23'] + data['X_24']) / 2
    center_y = (data['Y_23'] + data['Y_24']) / 2
    center_z = (data['Z_23'] + data['Z_24']) / 2

    coord = [col for col in data.columns if any(substr in col for substr in ['X_', 'Y_', 'Z_'])]
    # Нормализация позы относительно центра
    for col in coord:
        if 'X_' in col:
            data[col] -= center_x
        elif 'Y_' in col:
            data[col] -= center_y
            #data[col] *= -1
        elif 'Z_' in col:
            data[col] -= center_z
    #data.to_csv(r"DS\centr.csv", sep=';', index=False)

# Функция для построения скелета на каждом кадре
def update_skeleton(frame):
    ax.cla()  # Очистить ось
    lm = 1
    ax.set_xlim([-lm, lm])
    ax.set_ylim([-lm, lm])
    ax.set_zlim([-lm, lm])
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    # Получаем данные для текущего кадра
    frame_data = data.loc[frame, :]

    # Рисуем линии между суставами
    # qq=['X','Y','Z']
    for i in lines:
        ax.plot(
            [frame_data[f'X_{i[0]}'], frame_data[f'X_{i[1]}']],
            [frame_data[f'Y_{i[0]}'], frame_data[f'Y_{i[1]}']],
            [frame_data[f'Z_{i[0]}'], frame_data[f'Z_{i[1]}']],
        'r-')

# Создаем фигуру и ось
fig = plt.figure(figsize=(10, 16))
ax = plt.axes(projection='3d')
#ax.azim = 90
ax.view_init(elev=0, azim=0, roll=270) # Поворачиваем оси
# Создаем анимацию
frames = data.index.to_list()
ani = animation.FuncAnimation(fig, update_skeleton, frames=frames, interval=1, repeat=True)

# Отображаем анимацию
plt.show()