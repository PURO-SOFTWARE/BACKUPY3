import os
import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
from tkinter import messagebox, filedialog, Label, Entry, Button, simpledialog
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import json
import subprocess
from datetime import datetime
import sys

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt):
        super().__init__(parent)
        self.title(title)

        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icono.ico")
            image = Image.open(icon_path)
            self.icon = ImageTk.PhotoImage(image)
            self.tk.call('wm', 'iconphoto', self._w, self.icon)
        except Exception as e:
            print(f"No se pudo cargar la imagen del icono: {e}")

        self.label = Label(self, text=prompt)
        self.label.pack(pady=10)

        self.entry = Entry(self, show='*', width=45)
        self.entry.pack(pady=1, padx=20)

        self.button_ok = Button(self, text="OK", command=self.ok)
        self.button_ok.pack(pady=5)

    def ok(self):
        self.result = self.entry.get()
        self.destroy()

class ProgramaBackup(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("Programa de Backup")
        self.geometry("480x270")
        self.withdraw()
        self.icon_path = os.path.join(os.path.dirname(sys.argv[0]), "icono.ico")


        try:
            image = Image.open(self.icon_path)
            self.icon = ImageTk.PhotoImage(image)
            self.tk.call('wm', 'iconphoto', self._w, self.icon)
        except Exception as e:
            print(f"No se pudo cargar la imagen del icono: {e}")

        self.cargar_contrasena()
        self.mostrar_formulario()

    def guardar_contrasena(self, contrasena):
        data = {'contrasena': contrasena}
        with open('seguridad.json', 'w') as f:
            json.dump(data, f)

    def cargar_contrasena(self):
        try:
            with open('seguridad.json', 'r') as f:
                data = json.load(f)
                self.contrasena_almacenada = data.get('contrasena', '')
        except FileNotFoundError:
            self.contrasena_almacenada = ''

    def show_custom_dialog(self, title, prompt):
        dialog = CustomDialog(self, title, prompt)
        self.wait_window(dialog)
        return dialog.result

    def mostrar_formulario(self):
        self.deiconify()
        self.crear_interfaz()
        self.configurar_scheduler()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_programa)
        self.bind("<Visibility>", self.on_visibility)

    def on_visibility(self, event):
        if event.type == 19 and event.state == 1:
            self.iconify()

    def crear_interfaz(self):
        self.label_origen = Label(self, text="Origen:")
        self.label_origen.grid(row=0, column=0, sticky=tk.E)

        self.entry_origen = Entry(self, width=40)
        self.entry_origen.grid(row=0, column=1, padx=5, pady=5)

        self.button_origen = Button(self, text="Origen", command=self.seleccionar_origen, bg="#ccffcc", width=15)
        self.button_origen.grid(row=0, column=2, padx=5, pady=5)

        self.label_destino = Label(self, text="Destino:")
        self.label_destino.grid(row=1, column=0, sticky=tk.E)

        self.entry_destino = Entry(self, width=40)
        self.entry_destino.grid(row=1, column=1, padx=5, pady=5)

        self.button_destino = Button(self, text="Destino", command=self.seleccionar_destino, bg="#ccffcc", width=15)
        self.button_destino.grid(row=1, column=2, padx=5, pady=5)

        self.label_hora = Label(self, text="Hora de Backup:")
        self.label_hora.grid(row=2, column=0, sticky=tk.E)

        self.entry_hora = Entry(self, width=40)
        self.entry_hora.grid(row=2, column=1, padx=5, pady=5)

        self.button_hora = Button(self, text="Configurar Hora", command=self.configurar_hora, bg="#ccffcc", width=15)
        self.button_hora.grid(row=2, column=2, padx=5, pady=5)

        self.button_cambiar_contrasena = Button(self, text="Cambiar Contraseña", command=self.cambiar_contrasena, bg="#ccffcc", width=20)
        self.button_cambiar_contrasena.grid(row=4, column=0, columnspan=3, pady=5)

        self.label_resultado = Label(self, text="", font=("Arial", 14), fg="green")
        self.label_resultado.grid(row=5, column=0, columnspan=3, pady=5)

        self.cargar_configuracion()
        self.actualizar_label()

    def seleccionar_origen(self):
        self.validar_contrasena_y_ejecutar(self.cambiar_origen)

    def seleccionar_destino(self):
        self.validar_contrasena_y_ejecutar(self.cambiar_destino)

    def validar_contrasena_y_ejecutar(self, funcion_a_ejecutar):
        while True:
            input_contrasena = self.show_custom_dialog("Programa Backup", "Ingrese la contraseña:")
            if input_contrasena == self.contrasena_almacenada:
                funcion_a_ejecutar()
                break
            else:
                print("Contraseña incorrecta. Intenta de nuevo.")
        print("Contraseña correcta. Acceso permitido.")

    def cambiar_origen(self):
        directorio_origen = filedialog.askdirectory()
        self.habilitar_escritura(self.entry_origen)
        self.entry_origen.delete(0, tk.END)
        self.entry_origen.insert(0, directorio_origen)
        self.guardar_configuracion()
        self.inhabilitar_escritura(self.entry_origen)
        self.actualizar_label()

    def cambiar_destino(self):
        directorio_destino = filedialog.askdirectory()
        self.habilitar_escritura(self.entry_destino)
        self.entry_destino.delete(0, tk.END)
        self.entry_destino.insert(0, directorio_destino)
        self.guardar_configuracion()
        self.inhabilitar_escritura(self.entry_destino)
        self.actualizar_label()

    def configurar_hora(self):
        self.validar_contrasena_y_ejecutar(self.realizar_configuracion_hora)

    def realizar_configuracion_hora(self):
        def validar_hora(input_hora):
            try:
                horas, minutos = map(int, input_hora.split(':'))
                if 0 <= horas <= 23 and 0 <= minutos <= 59:
                    horas_formateadas = f'{horas:02d}'
                    minutos_formateados = f'{minutos:02d}'
                    hora_formateada = f'{horas_formateadas}:{minutos_formateados}'
                    return hora_formateada
                else:
                    return False
            except ValueError:
                return False

        hora_configurada = self.show_custom_dialog("Configurar Hora", "Ingrese la hora (formato 24 horas):\nHH:MM")

        while hora_configurada is not None and not validar_hora(hora_configurada):
            hora_configurada = self.show_custom_dialog("Configurar Hora", "Formato de hora incorrecto. Ingrese la hora (formato 24 horas):\nHH:MM")

        self.habilitar_escritura(self.entry_hora)
        if hora_configurada is not None:
            self.entry_hora.delete(0, tk.END)
            self.entry_hora.insert(0, validar_hora(hora_configurada))
            self.guardar_configuracion()
        self.inhabilitar_escritura(self.entry_hora)

    def habilitar_escritura(self, entry):
        entry.config(state='normal')

    def inhabilitar_escritura(self, entry):
        entry.config(state='readonly')

    def cargar_configuracion(self):
        try:
            with open('configuracion.json', 'r') as f:
                configuracion = json.load(f)
                self.entry_origen.insert(0, configuracion.get('origen', ''))
                self.entry_destino.insert(0, configuracion.get('destino', ''))
                self.entry_hora.insert(0, configuracion.get('hora', ''))
                self.inhabilitar_escritura(self.entry_origen)
                self.inhabilitar_escritura(self.entry_destino)
                self.inhabilitar_escritura(self.entry_hora)
        except FileNotFoundError:
            pass

    def guardar_configuracion(self):
        configuracion = {
            'origen': self.entry_origen.get(),
            'destino': self.entry_destino.get(),
            'hora': self.entry_hora.get()
        }
        with open('configuracion.json', 'w') as f:
            json.dump(configuracion, f)

    def configurar_scheduler(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.add_job(self.ejecutar_backup, trigger=CronTrigger.from_crontab('* * * * *'))
        self.scheduler.start()

    def ejecutar_backup(self):
        hora_programada = self.entry_hora.get()
        hora_actual = datetime.now()

        if hora_programada == hora_actual.strftime('%H:%M'):
            origen = self.entry_origen.get()
            destino = self.entry_destino.get()

            try:
                mensaje_proceso = f"Realizando Backup, espere un momento..."
                print(mensaje_proceso)
                self.label_resultado.config(text=mensaje_proceso, fg="red")
                subprocess.run(['xcopy', os.path.normpath(origen), os.path.normpath(destino), '/e', '/c', '/k', '/y'], check=True)
                mensaje = f"Último Backup realizado: {hora_actual.strftime('%Y-%m-%d %H:%M:%S')}"
                print(mensaje)
                self.label_resultado.config(text=mensaje, fg="green")
            except subprocess.CalledProcessError as e:
                mensaje_error = f"Error durante el backup: {str(e)}"
                print(mensaje_error)
                self.label_resultado.config(text=mensaje_error, fg="red")

        self.actualizar_label()

    def cambiar_contrasena(self):
        if self.validar_contrasena_actual():
            nueva_contrasena = self.pedir_contrasena()
            self.guardar_contrasena(nueva_contrasena)
            self.contrasena_almacenada = nueva_contrasena
            print("Contraseña cambiada exitosamente.")
            messagebox.showinfo("Éxito", "Contraseña modificada con éxito.")
        else:
            print("Contraseña actual incorrecta. Intenta de nuevo.")
            messagebox.showwarning("Error", "Contraseña actual incorrecta. No se pudo cambiar la contraseña.")

    def validar_contrasena_actual(self):
        input_contrasena_actual = self.show_custom_dialog("Programa Backup", "Ingrese la contraseña actual:")
        return input_contrasena_actual == self.contrasena_almacenada

    def pedir_contrasena(self):
        nueva_contrasena = self.show_custom_dialog("Nueva Contraseña", "Ingrese una nueva contraseña:")
        confirmar_contrasena = self.show_custom_dialog("Confirmar Contraseña", "Confirme la nueva contraseña:")

        while nueva_contrasena != confirmar_contrasena:
            print("Las contraseñas no coinciden. Intenta de nuevo.")
            nueva_contrasena = self.show_custom_dialog("Nueva Contraseña", "Ingrese una nueva contraseña:")
            confirmar_contrasena = self.show_custom_dialog("Confirmar Contraseña", "Confirme la nueva contraseña:")

        return nueva_contrasena

    def cerrar_programa(self):
        self.scheduler.shutdown()
        self.destroy()

    def actualizar_label(self):
        for widget in self.grid_slaves():
            if int(widget.grid_info()["row"]) == 3:
                widget.destroy()

        origen = self.entry_origen.get()
        destino = self.entry_destino.get()
        hora_programada = self.entry_hora.get()

        horas, minutos = map(int, hora_programada.split(':'))
        hora_formateada = f'{horas:02d}:{minutos:02d}'

        info = f"Origen: {origen}\nDestino: {destino}\nBackup programado a las: {hora_formateada}"
        label_info = Label(self, text=info)
        label_info.grid(row=3, column=0, columnspan=3, pady=10)

if __name__ == "__main__":
    app = ProgramaBackup()
    app.iconify()  # Minimiza la ventana al inicio
    app.mainloop()
