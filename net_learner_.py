import os
import numpy as np
import pandas as pd
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
import tensorflow as tf
from tensorflow.keras.utils import Sequence , plot_model
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Dense, Dropout, LSTM
from tensorflow.keras.metrics import MeanSquaredError, BinaryAccuracy
from tensorflow.keras.initializers import GlorotUniform
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler, MinMaxScaler

import joblib


import tensorflow.keras.backend as K

import matplotlib.pyplot as plt



class DataGenerator(Sequence):
    
    def __init__(self, file_paths, window_size, step_size, batch_size=32, shuffle=False, x_cols=None, y_cols=None, center_scaler_path='center_scaler.gz'):
        super(DataGenerator, self).__init__()
        self.file_paths = file_paths
        self.window_size = window_size
        self.step_size = step_size
        self.batch_size = batch_size
        self.shuffle = shuffle
        self.x_cols = x_cols
        self.y_cols = y_cols
        self.center_scaler_path = center_scaler_path
        self.center_scaler = None
        self.load_or_initialize_center_scaler()
        self.windows = []
        for path in file_paths:
            self.windows.extend(self.load_and_preprocess_data(path))
        self.on_epoch_end()

    def load_or_initialize_center_scaler(self):
        if os.path.exists(self.center_scaler_path):
            self.center_scaler = joblib.load(self.center_scaler_path)
        else:
            self.center_scaler = MinMaxScaler(feature_range=(-4, 4))

    def load_and_preprocess_data(self, file_path):
        df = pd.read_csv(file_path)
        # Вычисляем среднюю точку между бедрами
        center_x = (df['left_hip_X'] + df['right_hip_X']) / 2
        center_y = (df['left_hip_Y'] + df['right_hip_Y']) / 2
        center_z = (df['left_hip_Z'] + df['right_hip_Z']) / 2

        # Нормализация позы относительно центра
        for col in df.columns:
            if '_X' in col:
                df[col] -= center_x
            elif '_Y' in col:
                df[col] -= center_y
            elif '_Z' in col:
                df[col] -= center_z

        # Добавляем отнормированные координаты центра
        center_coords = np.stack((center_x, center_y, center_z), axis=-1)
        #if not hasattr(self, 'center_fitted'):
        #    self.center_scaler.fit(center_coords)
        #    joblib.dump(self.center_scaler, self.center_scaler_path)
        #    self.center_fitted = True
        #center_coords = self.center_scaler.transform(center_coords)

        # Обновляем данные X

        x_data = df.iloc[:, self.x_cols].values

        x_data = np.hstack((x_data, center_coords))
        y_data = df.iloc[:, self.y_cols].values
        
        windows = []
        for start in range(0, len(df) - self.window_size + 1, self.step_size):
            end = start + self.window_size
            windows.append((x_data[start:end], y_data[end-1]))
        return windows

    def __len__(self):
        return int(np.ceil(len(self.windows) / self.batch_size))

    def __getitem__(self, index):
        batch_x = []
        batch_y = {'kata_output': [], 'element_output': [], 'binary_outputs': []}

        start = index * self.batch_size
        end = min(start + self.batch_size, len(self.windows))
        for i in range(start, end):
            window_x, window_y = self.windows[i]
            batch_x.append(window_x)
            batch_y['kata_output'].append(window_y[0])
            batch_y['element_output'].append(window_y[1])
            batch_y['binary_outputs'].append(window_y[2:])

        # Проверка данных перед возвращением
        x_array = np.array(batch_x)
        if np.isnan(x_array).any() :
            print("\nNaN in x_batch:", np.isnan(x_array).any())
            

            reshaped_array = x_array.reshape(x_array.shape[0], -1)
            pd.DataFrame(reshaped_array).to_csv('problematic_data.csv', index=False)            
            print(x_array)
        if np.isinf(x_array).any() :    
            print("\nInf in x_batch:", np.isinf(x_array).any())
            print(x_array)
        
        return np.array(batch_x), {
            'kata_output': np.array(batch_y['kata_output']),
            'element_output': np.array(batch_y['element_output']),
            'binary_outputs': np.array(batch_y['binary_outputs'])
        }

    def on_epoch_end(self):
        if self.shuffle:
            np.random.shuffle(self.windows)

# 
# _____________________________________________________________________________________
#_______|_______|_______|_______|_______|_______|_______|_______|_______|_______|_______|_______|


# Формирование списка файлов 
# Пути к файлам для тренировки и валидации
dirDS = "DS"    # путь к датасету
DATASET = os.path.join(dirDS, 'DATASET')

train_DS = [2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 15, 17, 18, 19, 20]
val_DS = [1, 6, 11]  # 16  -  не корректый файл со второй камеры

#rain_DS = [8,9,10,12,13,14,15,16,17,18,19,20]
#val_DS = [3]

# Пути к файлам для тренировки
train_files = [os.path.join(DATASET, f'YX_DS{i:02d}.csv') for i in train_DS]
# Пути к файлам для валидации
val_files = [os.path.join(DATASET, f'YX_DS{i:02d}.csv') for i in val_DS]



# Настройки индексов столбцов для X и Y
x_columns = list(range(43,119,1))  # Используем  столбцов с 44 по 120  T, (X,Y,Z)*25 - 3D  поза после треангуляции и фильтрации  для X
y_columns = [2, 5]    # Используем столбцы 3 - номер ката, 6 - номер элемента  в ката 
y_columns = y_columns + list(range(6,39,1))  # Используем выбранные признаки 


# Обучение модели
#model.fit(train_generator, validation_data=val_generator, epochs=10)


# Демонстрация модели
#predictions = model.predict(val_generator)
# Здесь можно оценить результаты предсказаний, например, сравнив их с истинными значениями или визуализируя результаты.


# ТЕСТИРОВАНИЕ Создание генератора
train_generator_1 = DataGenerator(train_files, window_size=60, step_size=1, batch_size=1, shuffle=False, x_cols=x_columns, y_cols=y_columns)

# Получение и вывод первого батча данных
x_batch, y_batch = train_generator_1[0]
print("X batch shape:", x_batch.shape)
print("Y batch shape:", y_batch)
print("First X batch data example:", x_batch[0])
#print("First Y batch data example:", y_batch[0])

#Макро параметры
Window_size=6 
Step_size=1 
Batch_size=5

# Создание датагенераторов
train_generator = DataGenerator(train_files, window_size=Window_size, step_size=Step_size, batch_size=Batch_size, shuffle=False, x_cols=x_columns, y_cols=y_columns)
val_generator = DataGenerator(val_files,  window_size=Window_size, step_size=Step_size, batch_size=Batch_size, shuffle=False, x_cols=x_columns, y_cols=y_columns)
#------------------------------------------------------------------------------------------------------------------
#       Определение модели 
#------------------------------------------------------------------------------------------------------------------

# Параметры модели
num_features = 76 + 3  # Время + 25 точек * 3 координаты (x, y, z) + 3 (x, y, z) координаты центра
num_binary = 33    # 33 бинарных признаков
num_regression = 2 # 2 числовых выхода
#total_katas = 4    # 4 разных ката
#total_elements = 20 # 20 элементов в ката

Epochs = 200
#---------------------------------------------------------------------------------------------------

# Определение параметров модели

num_kata = 5       # Количество различных кат
num_elements = 22  # Количество элементов в каждом ката

# Входные данные
input_shape = (Window_size, num_features)
input_layer = Input(shape=input_shape)

# LSTM слой
lstm_out = LSTM(50, kernel_initializer=GlorotUniform(), return_sequences=False)(input_layer)

# Полносвязные слои для различных выходов
kata_output = Dense(num_kata, activation='softmax', kernel_initializer=GlorotUniform(), name='kata_output')(lstm_out)
element_output = Dense(num_elements, activation='softmax', name='element_output')(lstm_out)
binary_outputs = Dense(num_binary, activation='sigmoid', name='binary_outputs')(lstm_out)

# Собираем все выходы
outputs = [kata_output, element_output, binary_outputs]

# Создание модели
model = Model(inputs=input_layer, outputs=outputs)

# Оптимизатор
optimizer = Adam(learning_rate=0.01, clipnorm=1.0)

# Компиляция модели с несколькими потерями и метриками
model.compile(
    optimizer=optimizer,
    loss={
        'kata_output': 'sparse_categorical_crossentropy',
        'element_output': 'sparse_categorical_crossentropy',
        'binary_outputs': 'binary_crossentropy'  # Общий слой для всех бинарных признаков
    },
    metrics={
        'kata_output': 'accuracy',
        'element_output': 'accuracy',
        'binary_outputs': 'accuracy'  # Метрика для общего слоя бинарных выходов
    }
)

# Вывод информации о модели
model.summary()

#---------------------------------------------------------------------------------------------------






# Визуализация модели
#plot_model(model, show_shapes=True, show_layer_names=True)
#model.summary()



# Обучение модели

# Теперь, когда у вас 37 выходов и 37 метрик, вы можете без проблем запускать обучение:
history = model.fit(train_generator, validation_data=val_generator, epochs=Epochs)
#model.fit(x=train_inputs, y={'output1': train_labels1, 'output2': train_labels2}, ...)


# Создание нового графика
plt.figure(figsize=(12, 6))  # Установка размеров графика

# Графики потерь на обучающей и валидационной выборках
plt.subplot(1, 2, 1)  # Разделение области графика на 1 строку и 2 столбца, выбор первой области
plt.plot(history.history['loss'], label='Обучающая выборка')
plt.plot(history.history['val_loss'], label='Валидационная выборка')
plt.xlabel('Эпоха')
plt.ylabel('Потери')
plt.title('График потерь')
plt.legend()

# Графики точности на обучающей и валидационной выборках
plt.subplot(1, 2, 2)  # Выбор второй области
plt.plot(history.history['kata_output_accuracy'], label='Точность категории (обучение)')
plt.plot(history.history['val_kata_output_accuracy'], label='Точность категории (валидация)')
plt.plot(history.history['element_output_accuracy'], label='Точность элемента (обучение)')
plt.plot(history.history['val_element_output_accuracy'], label='Точность элемента (валидация)')
plt.plot(history.history['binary_outputs_accuracy'], label='Точность бинарных выходов (обучение)')
plt.plot(history.history['val_binary_outputs_accuracy'], label='Точность бинарных выходов (валидация)')
plt.xlabel('Эпоха')
plt.ylabel('Точность')
plt.title('График точности')
plt.legend()

# Сохранение графика в файл
plt.savefig('combined_plots.png')

# Отображение графика
plt.show()