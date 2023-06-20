import json
import re
import psycopg2
from tabnanny import check
from tkinter import *
from tkinter import ttk
from itertools import product
from operator import index
from tkinter.messagebox import showerror, showwarning, showinfo


# Подключение к Базе Данных
conn = psycopg2.connect(database="postgres", user="postgres", password="4444", host="localhost", port="5432") 
cur = conn.cursor()

# Создание таблиц
cur.execute("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, code_sosud INT, service VARCHAR(255), face VARCHAR(255), fio_or_name VARCHAR(255))")
cur.execute("CREATE TABLE IF NOT EXISTS fiz_face (id SERIAL PRIMARY KEY, fio VARCHAR(255), mail VARCHAR(255), date VARCHAR(255), seria_num_pass INT, tel_number INT)")
cur.execute("CREATE TABLE IF NOT EXISTS ur_face (id SERIAL PRIMARY KEY, fio_admin VARCHAR(255), fio_contact VARCHAR(255), rs VARCHAR(255), inn VARCHAR(255), tel_contact INT, bik VARCHAR(255), email VARCHAR(255))")
conn.commit()


window = Tk()  
window.title("Учет склада фабрики")  
window.geometry('400x200')

# убрать возможность изменять размер окна
window.resizable(False, False)


# Валдиция кода сосуда
def is_valid_numprod(newval):
    result=  re.match("^\d{0,9}$", newval) is not None
    if not result and len(newval) <= 9:
        showerror(title="Ошибка", message="Код сосуда должен быть корректным! Например: 123456789")
    else:
        pass
    return result
check_numprod = (window.register(is_valid_numprod), "%P")

# Валдиция для ФИО или Компании
def is_valid_name(newval):
    result=  re.match("[А-ЯЁ а-яё A-Z a-z]", newval) is not None
    if not result and len(newval) <= 10:
        showerror(title="Ошибка", message="ФИО должено быть корректным! Например: Иванов Иван Иванович")
    else:
        pass
    return result
check_name = (window.register(is_valid_name), "%S")

# Валдиция для электронной почты
def is_valid_email(newval):
    result=  re.match("[A-Z a-z 0-9 _.@-]+$", newval) is not None
    if not result and len(newval) <= 30:
        showerror(title="Ошибка", message="Почта должна быть корректной! Например: email@email.com")
    else:
        pass
    return result
check_email = (window.register(is_valid_email), "%S")

# Валидация для даты рождения
def is_valid_birthdate(newval):
    result=  re.match("^\d{0,2}(\.\d{0,2}){0,4}$", newval) is not None
    if not result and len(newval) <= 8:
        showerror(title="Ошибка", message="Дата рождения должна содержать только цифры и точку!")
    else:
        pass
    return result
check_birthdate = (window.register(is_valid_birthdate), "%P")

# Валдиция паспорта
def is_valid_passport(newval):
    result=  re.match("^\d{0,9}$", newval) is not None
    if not result and len(newval) <= 10:
        showerror(title="Ошибка", message="Паспорт должен быть верным! Например: 1234567890")
    else:
        pass
    return result
check_passport = (window.register(is_valid_passport), "%P")

# Валдиция для номера телефона
def is_valid_number(newval):
    result=  re.match("^\+{0,1}\d{0,11}$", newval) is not None
    if not result and len(newval) <= 12:
        showerror(title="Ошибка", message="Номер телефона должен быть корректным! Например: +79123456789")
    else:
        pass
    return result
check_number = (window.register(is_valid_number), "%P")

numprod = Label(window, text="Код сосуда")
numprod.grid(column = 1, row = 1, padx = 5, pady = 5)
input_sosud = Entry(window, width=20, validate="key", validatecommand=check_numprod)
input_sosud.grid(column = 2, row = 1, padx = 5, pady = 5)

# Подсказка сосуда
cur.execute("SELECT code_sosud FROM orders ORDER BY id DESC LIMIT 1")
for record in cur:
    input_sosud.insert(0, record[0])

services = Label(window, text="Желаемые услуги")
services.grid(column = 1, row = 2, padx = 5, pady = 5)
input_uslugi = Entry(window, width=20)
input_uslugi.grid(column = 2, row = 2, padx = 5, pady = 5)

var1 = BooleanVar()
var2 = BooleanVar()
# Функция отключения противоположного inpitbox
def on_checkbox_toggle(var):
       if var.get():
        if var == var1:
            var2.set(False)
        elif var == var2:
            var1.set(False)
        
choice = Label(window, text="Физ.лицо или юр.лицо")
choice.grid(column = 1, row = 3, padx = 5, pady = 5)
enabled_checkbutton_yur = Checkbutton(window, text="ЮЛ", variable=var1, command=lambda: on_checkbox_toggle(var1))
enabled_checkbutton_yur.grid(column = 2, row = 3, padx = 5, pady = 5)
enabled_checkbutton_fz = Checkbutton(window, text="ФЛ", variable=var2, command=lambda: on_checkbox_toggle(var2))
enabled_checkbutton_fz.grid(column = 3, row = 3, padx = 5, pady = 5)

text_name = Label(window, text="ФИО ваше или руководителя")
text_name.grid(column = 1, row = 4, padx = 5, pady = 5)
input_name = Entry(window, width=20, validate="key", validatecommand=check_name)
input_name.grid(column = 2, row = 4, padx = 5, pady = 5)

button_send = Button(window, text="Отправить", command=lambda: register())
button_send.grid(column = 2, row = 5, padx = 5, pady = 5)

def register():
    isRegister = False
    
    # ЕСЛИ var1 == true то запрос к юрлицам в обратном случае к физлицам
    if var1.get():
        cur.execute("SELECT fio_admin FROM ur_face")
    else:
        cur.execute("SELECT fio FROM fiz_face")
    
    # пробег по рез-ам запроса если совпало то флаг isRegister в true
    for record in cur:
        if input_name.get() == record[0]:
            isRegister = True
            break
    
    # если юзер есть то проверка физ или юр и кидаем заказ
    if isRegister:
        name = input_name.get()
        service = input_uslugi.get()
        code_sosud = input_sosud.get()
        
        if var1.get():
            face = "ur"
        else:
            face = "fiz"
            
        cur.execute("INSERT INTO orders (code_sosud, service, face, fio_or_name) VALUES (%s, %s, %s, %s)", (code_sosud, service, face, name))
        conn.commit()
    # если нет то проверка юр или физ и вызов соотв. регистрации
    else:
        if var1.get():
            create_window_urface(window)
        else:
            create_window_fizface(window)
     

def create_window_fizface(window):
    window3 = Toplevel(window)
    window3.title("Регистрация нового физ.лица")  
    window3.geometry('450x400') 
    # убрать возможность изменять размер окна
    window3.resizable(False, False)

    text_name = Label(window3, text="ФИО")
    text_name.grid(column = 1, row = 1, padx = 5, pady = 5)
    input_name = Entry(window3, width=20, validate="key", validatecommand=check_name)
    input_name.grid(column = 2, row = 1, padx = 5, pady = 5)

    text_email = Label(window3, text="Эл.почта")
    text_email.grid(column = 1, row = 2, padx = 5, pady = 5)
    input_email = Entry(window3, width=20, validate="key", validatecommand=check_email)
    input_email.grid(column = 2, row = 2, padx = 5, pady = 5)

    text_date = Label(window3, text="Дата рождения")
    text_date.grid(column = 1, row = 3, padx = 5, pady = 5)
    input_date = Entry(window3, width=20, validate="key", validatecommand=check_birthdate)
    input_date.grid(column = 2, row = 3, padx = 5, pady = 5)

    text_password = Label(window3, text="Серия и номер")
    text_password.grid(column = 1, row = 4, padx = 5, pady = 5)
    input_passport = Entry(window3, width=20, validate="key", validatecommand=check_passport)
    input_passport.grid(column = 2, row = 4, padx = 5, pady = 5)

    text_number = Label(window3, text="Номер телефона")
    text_number.grid(column = 1, row = 5, padx = 5, pady = 5)
    input_telephone = Entry(window3, width=20, validate="key", validatecommand=check_number)
    input_telephone.grid(column = 2, row = 5, padx = 5, pady = 5)

    
    button_reg = Button(window3, text="Зарегистрировать физ.лицо и отправить", command=lambda: register_fizface())
    button_reg.grid(column = 2, row = 6, padx = 5, pady = 5)

    def register_fizface():
        name=input_name.get()
        email=input_email.get()
        date=input_date.get()
        passport=input_passport.get()
        telephone=input_telephone.get()
        cur.execute("INSERT INTO fiz_face (fio,mail,date,seria_num_pass,tel_number) VALUES (%s, %s, %s, %s, %s)", (name,email,date,passport,telephone))
        conn.commit()

def create_window_urface(window):
    window4 = Toplevel(window)
    window4.title("Регистрация нового юр.лица")  
    window4.geometry('450x400') 
    # убрать возможность изменять размер окна
    window4.resizable(False, False)

    name_leader = Label(window4, text="ФИО руководителя")
    name_leader.grid(column = 1, row = 1, padx = 5, pady = 5)
    input_name_leader = Entry(window4, width=20, validate="key", validatecommand=check_name)
    input_name_leader.grid(column = 2, row = 1, padx = 5, pady = 5)

    name_contact = Label(window4, text="ФИО контактного лица")
    name_contact.grid(column = 1, row = 2, padx = 5, pady = 5)
    input_name_contact = Entry(window4, width=20, validate="key", validatecommand=check_name)
    input_name_contact.grid(column = 2, row = 2, padx = 5, pady = 5)

    text_pc = Label(window4, text="р/с")
    text_pc.grid(column = 1, row = 3, padx = 5, pady = 5)
    input_pc = Entry(window4, width=20, validate="key", validatecommand=check_numprod)
    input_pc.grid(column = 2, row = 3, padx = 5, pady = 5)

    text_inn = Label(window4, text="ИНН")
    text_inn.grid(column = 1, row = 4, padx = 5, pady = 5)
    input_inn = Entry(window4, width=20, validate="key", validatecommand=check_numprod)
    input_inn.grid(column = 2, row = 4, padx = 5, pady = 5)

    number_contact = Label(window4, text="Тел.ном контактного лица")
    number_contact.grid(column = 1, row = 5, padx = 5, pady = 5)
    input_number_contact = Entry(window4, width=20, validate="key", validatecommand=check_number)
    input_number_contact.grid(column = 2, row = 5, padx = 5, pady = 5)

    text_bik = Label(window4, text="БИК")
    text_bik.grid(column = 1, row = 6, padx = 5, pady = 5)
    input_bik = Entry(window4, width=20, validate="key", validatecommand=check_numprod)
    input_bik.grid(column = 2, row = 6, padx = 5, pady = 5)

    text_email = Label(window4, text="Эл.почта")
    text_email.grid(column = 1, row = 7, padx = 5, pady = 5)
    input_email = Entry(window4, width=20, validate="key", validatecommand=check_email)
    input_email.grid(column = 2, row = 7, padx = 5, pady = 5)

    but6 = Button(window4, text="Зарегистрировать юр.лицо и отправить", command=lambda: register_urface())
    but6.grid(column = 2, row = 8, padx = 5, pady = 5)

    def register_urface():
        email = input_email.get()
        bik = input_bik.get()
        num_c = input_number_contact.get()
        inn = input_inn.get()
        pc = input_pc.get()
        name_cont = input_name_contact.get()
        name_lead = input_name_leader.get()
        cur.execute("INSERT INTO ur_face (fio_admin, fio_contact, rs, inn, tel_contact, bik, email) VALUES (%s, %s, %s, %s, %s, %s, %s)", (name_lead, name_cont, pc, inn, num_c, bik, email))
        conn.commit()

window.mainloop()