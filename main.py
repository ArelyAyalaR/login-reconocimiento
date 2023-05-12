import os.path
import pickle

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition
import subprocess
import util
import mysql.connector
import datetime

# Conexión a la base de datos
cnx = mysql.connector.connect(user='root', password='03052003',
                              host='127.0.0.1',
                              database='biblioteca')
cursor = cnx.cursor()

class App:
    def __init__(self):
        # Base de Datos XD

        self.main_window = tk.Tk()
        self.main_window.geometry("1200x520+350+100")

        self.login_button_main_window = util.get_button(self.main_window, 'login', 'green', self.login)
        self.login_button_main_window.place(x=750, y=200)

        self.logout_button_main_window = util.get_button(self.main_window, 'logout', 'red', self.logout)
        self.logout_button_main_window.place(x=750, y=300)

        self.register_new_user_button_main_window = util.get_button(self.main_window, 'register new user', 'gray',
                                                                    self.register_new_user, fg='black')
        self.register_new_user_button_main_window.place(x=750, y=400)

        self.webcam_label = util.get_img_label(self.main_window)
        self.webcam_label.place(x=10, y=0, width=700, height=500)

        self.add_webcam(self.webcam_label)

        self.db_dir = './db'
        if not os.path.exists(self.db_dir):
            os.mkdir(self.db_dir)

        self.log_path = './log.txt'

    def get_user_code(self, name):
        query = 'SELECT codigo FROM alumnos WHERE nombre = %s'
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def get_user_id(self, name):
        query = "SELECT id FROM usuarios WHERE nombre = %s"
        cursor.execute(query, (name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 0

    def add_webcam(self, label):
        if 'cap' not in self.__dict__:
            self.cap = cv2.VideoCapture(0)

        self._label = label
        self.process_webcam()

    def process_webcam(self):
        ret, frame = self.cap.read()

        self.most_recent_capture_arr = frame
        img_ = cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)
        self.most_recent_capture_pil = Image.fromarray(img_)
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        self._label.imgtk = imgtk
        self._label.configure(image=imgtk)

        self._label.after(20, self.process_webcam)

    def login(self):
        ruta_exe = 'C:/Users/Lenovo/Documents/Biblioteca_Project/Biblioteca-/BibliotecaProject/bin/Debug/net6.0-windows/BibliotecaProject.exe'
        name = util.recognize(self.most_recent_capture_arr, self.db_dir)
        codigo = self.get_user_code(name)

        # Gente Biblioteca
        query = 'INSERT INTO gente_biblioteca (codigoA) VALUES (%s)'
        values = (codigo,)
        cursor.execute(query, values)
        cnx.commit()

        # Agregue un nuevo registro a la tabla historial
        query = 'INSERT INTO historial_gente_biblioteca (codigoAA, hora_ingreso) VALUES (%s, %s)'
        values = (codigo, datetime.datetime.now())
        cursor.execute(query, values)
        cnx.commit()

        if name in ['Persona desconocida', 'Ninguna persona encontrada']:
            util.msg_box('Ups', 'Usuario desconocido. Por favor registra un nuevo usuario o intenta de nuevo.')
        else:
            util.msg_box('Bienvenido de vuelta', 'Bienvenid@, {}.'.format(name))
            subprocess.call([ruta_exe])
            with open(self.log_path, 'a') as f:
                f.write('{},{},in\n'.format(name, datetime.datetime.now()))
                f.close()

    def logout(self):

        name = util.recognize(self.most_recent_capture_arr, self.db_dir)
        codigo = self.get_user_code(name)
        id = self.get_user_id(name)

        query = "INSERT INTO salidas (nombre, codigoAlumn) VALUES (%s, %s)"
        values = (name, codigo,)
        cursor.execute(query, values)
        cnx.commit()

        # Agregue un nuevo registro a la tabla historial
        query = 'UPDATE historial_gente_biblioteca SET hora_salida = %s WHERE codigoAA = %s ORDER BY id DESC LIMIT 1'
        values = (datetime.datetime.now(), codigo,)
        cursor.execute(query, values)
        cnx.commit()

        # Eliminación de registro de login en la tabla gente_biblioteca_b
        query = "DELETE FROM gente_biblioteca WHERE codigoA=%s"
        values = (codigo,)
        cursor.execute(query, values)
        cnx.commit()


        if name in ['Persona desconocida', 'Personas no encontradas.']:
            util.msg_box('Ups', 'Usuario desconocido. Por favor registra un nuevo usuario o intenta de nuevo.')
        else:
            util.msg_box('Hasta la vista', 'Adiós, {}.'.format(name))
            with open(self.log_path, 'a') as f:
                f.write('{},{},out\n'.format(name, datetime.datetime.now()))
                f.close()

    def register_new_user(self):
        self.register_new_user_window = tk.Toplevel(self.main_window)
        self.register_new_user_window.geometry("1200x520+370+120")

        self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Accept', 'green', self.accept_register_new_user)
        self.accept_button_register_new_user_window.place(x=750, y=300)

        self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Try again', 'red', self.try_again_register_new_user)
        self.try_again_button_register_new_user_window.place(x=750, y=400)

        self.capture_label = util.get_img_label(self.register_new_user_window)
        self.capture_label.place(x=10, y=0, width=700, height=500)

        self.add_img_to_label(self.capture_label)

        self.entry_text_register_new_user = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user.place(x=750, y=190)

        self.text_label_register_new_user = util.get_text_label(self.register_new_user_window, 'Por favor, \ningresa tu nombre:')
        self.text_label_register_new_user.place(x=750, y=130)

        # Ingreso de código
        self.entry_text_register_new_user_codigo = util.get_entry_text(self.register_new_user_window)
        self.entry_text_register_new_user_codigo.place(x=750, y=80)

        self.text_label_register_new_user_codigo = util.get_text_label(self.register_new_user_window, 'Por favor, \ningresa tu código:')
        self.text_label_register_new_user_codigo.place(x=750, y=20)

        # Crear variable de control para el checkbutton
        self.is_admin = tk.BooleanVar()

        # Crear checkbutton para indicar si es un administrador o no
        self.admin_checkbutton = tk.Checkbutton(self.register_new_user_window, text="Administrador",
                                                variable=self.is_admin)
        self.admin_checkbutton.pack()
        self.admin_checkbutton.place(x=750, y=270)
    def try_again_register_new_user(self):
        self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
        imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)
        label.imgtk = imgtk
        label.configure(image=imgtk)

        self.register_new_user_capture = self.most_recent_capture_arr.copy()

    def start(self):
        self.main_window.mainloop()

    def accept_register_new_user(self):
        is_admin = self.is_admin.get()
        name = self.entry_text_register_new_user.get(1.0, "end-1c")
        codigo = self.entry_text_register_new_user_codigo.get(1.0, "end-1c")
        #id = self.get_user_id(name)
        embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]

        file = open(os.path.join(self.db_dir, '{}.pickle'.format(name)), 'wb')
        pickle.dump(embeddings, file)

        # Inserta la información en la tabla usuarios
        query = "INSERT INTO usuarios (nombre, codigoAlumm, esAdmin) VALUES  (%s, %s, %s)"
        cursor.execute(query, (name, codigo, is_admin))
        cnx.commit()

        util.msg_box('¡Éxito!', 'usuario registrado correctamente!')

        self.register_new_user_window.destroy()


if __name__ == "__main__":
    app = App()
    app.start()
