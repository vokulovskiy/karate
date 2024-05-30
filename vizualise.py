import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

frame = 100

fn1=r'DS\DATASET\YX_DS01.csv'
df1 = pd.read_csv(fn1)
x1 = df1.loc[frame,[col for col in df1.columns if '_X' in col]].to_list()
y1 = df1.loc[frame,[col for col in df1.columns if '_Y' in col]].to_list()
z1 = df1.loc[frame,[col for col in df1.columns if '_Z' in col]].to_list()
fn2 = r"C:\temp\Cam_1_1920x1080x60\20240209_181457.csv"
df2 = pd.read_csv(fn2)
x2 = df2.loc[frame,[col for col in df2.columns if 'X_' in col]].to_list()
y2 = df2.loc[frame,[col for col in df2.columns if 'Y_' in col]].to_list()
z2 = df2.loc[frame,[col for col in df2.columns if 'Z_' in col]].to_list()
# Создание первого графика
fig1 = plt.figure()
ax1 = fig1.add_subplot(111, projection='3d')
ax1.scatter(x1, y1, z1, c='r', marker='o')
ax1.set_xlabel('X')
ax1.set_ylabel('Y')
ax1.set_zlabel('Z')
ax1.set_title('Первый 3D график')

# Создание второго графика
fig2 = plt.figure()
ax2 = fig2.add_subplot(111, projection='3d')
ax2.scatter(x2, y2, z2, c='b', marker='^')
ax2.set_xlabel('X')
ax2.set_ylabel('Y')
ax2.set_zlabel('Z')
ax2.set_title('Второй 3D график')
plt.show()
print(df1.columns.to_list())