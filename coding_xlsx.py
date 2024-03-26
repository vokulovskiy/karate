import pandas as pd
import os

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

def cr_label(n_el, code, len_l, labels):
    lbl = str(n_el).zfill(3) +'0'*(len_l-3)
    for s in code.split('_'):
        try:
            ind = labels.index(s.strip())+2
            lbl = lbl[:ind]+'1'+lbl[ind+1:]
        except:
            print('Invalid label', s)
    return lbl

fname = "Разметка видео.xlsx"
vfname = "video/elements.txt"
xlsx_file = pd.ExcelFile(fname)
sheet_names = xlsx_file.sheet_names
code_file = pd.read_excel("code.xlsx")
labels1, len_label = read_sd(vfname)
labels = [l.split(';')[1].split('|')[0].strip() for l in labels1]
commands = {}
elem_string = []
for i,row in code_file.iterrows():
    commands[row.name_el.strip()] = row.code.strip()
    elem_string += row.code.split('_')
# print(commands, sep='\n')
# '№ элемента', 'Название элемента', 'N start', 'N stop'

for sh in sheet_names:
    kata = pd.read_excel(fname,sh, skiprows=1)
    #print(sh)
    kata.fillna('', inplace=True)
    with open(sh.split('.')[0]+'.lbl','w') as f:
        for i,row in kata.iterrows():
            if (not isinstance(row['N start'],float)) or (not isinstance(row['N stop'],float)):
    #            print(isinstance(row['N start'],float))
                next
            else:
                n_start = int(float(row['N start']))
                n_stop = int(float(row['N stop']))
            n_el = 0
            if isinstance(row['№ элемента'],float):
                n_el = int(float(row['№ элемента']))
            
            try:
                el = commands[' '.join(row['Название элемента'].strip().split())]
                label = cr_label(n_el, el, len_label, labels)
                print(f'{n_start}-{n_stop}:{label}',file=f)
            except:
                if len(row['Название элемента'])==0:
                    break
                # print(row['Название элемента'])
#print(sorted(set(elem_string)))