
# Instalar dependencias
# pip install keyboard

import tkinter as tk
from tkinter import messagebox

import json
import os
import keyboard

from updater import comprobar_actualizacion
from notification import (
    mostrar_notificacion,
    limpiar_cola_notificaciones
)


VERSION = "1.0.0"

CONFIG_FILE = "config.json"


# --------------------------------
# CONFIGURACIÓN
# --------------------------------

def cargar_config():

    if not os.path.exists(CONFIG_FILE):
        return {
            "canal": ""
        }

    try:

        with open(CONFIG_FILE, "r", encoding="utf-8") as archivo:
            return json.load(archivo)

    except json.JSONDecodeError:

        return {
            "canal": ""
        }


def guardar_config():

    configuracion = {
        "canal": entrada_canal.get()
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as archivo:
        json.dump(
            configuracion,
            archivo,
            indent=4,
            ensure_ascii=False
        )


# --------------------------------
# MOSTRAR / ESCONDER UI
# --------------------------------

def alternar_ui():

    if ventana.state() == "withdrawn":

        ventana.deiconify()
        ventana.lift()
        ventana.focus_force()

    else:

        ventana.withdraw()

# --------------------------------
# CERRAR
# --------------------------------

def cerrar():

    guardar_config()

    keyboard.unhook_all_hotkeys()

    ventana.destroy()


# --------------------------------
# COMPROBAR ACTUALIZACIÓN
# --------------------------------

def comprobar_version():

    nueva_version = comprobar_actualizacion()

    if nueva_version:

        respuesta = messagebox.askyesno(
            "Actualización disponible",
            f"Hay una nueva versión disponible.\n\n"
            f"Actual: {VERSION}\n"
            f"Nueva: {nueva_version}\n\n"
            f"¿Querés actualizar?"
        )

        if respuesta:

            messagebox.showinfo(
                "Actualización",
                "La descarga de actualizaciones "
                "la implementaremos en la próxima etapa."
            )


# --------------------------------
# VENTANA
# --------------------------------

ventana = tk.Tk()

ventana.title("Streamer Interactions")

ventana.geometry("600x400")

ventana.protocol(
    "WM_DELETE_WINDOW",
    cerrar
)


# --------------------------------
# CARGAR CONFIG
# --------------------------------

configuracion = cargar_config()


# --------------------------------
# UI
# --------------------------------

titulo = tk.Label(
    ventana,
    text="Streamer Interactions",
    font=("Arial", 24)
)

titulo.pack(pady=30)


version = tk.Label(
    ventana,
    text=f"Versión {VERSION}"
)

version.pack()


# Canal

texto_canal = tk.Label(
    ventana,
    text="Nombre del canal:"
)

texto_canal.pack(pady=(30, 5))


entrada_canal = tk.Entry(
    ventana,
    width=40
)

entrada_canal.pack()

entrada_canal.insert(
    0,
    configuracion.get("canal", "")
)


# Guardar

boton_guardar = tk.Button(
    ventana,
    text="Guardar configuración",
    command=guardar_config
)

boton_guardar.pack(pady=15)


# Probar notificación

boton_prueba = tk.Button(
    ventana,
    text="Probar notificación",
    command=mostrar_notificacion
)

boton_prueba.pack(pady=10)

# Limpiar colas

boton_limpiar = tk.Button(
    ventana,
    text="Limpiar notificaciones en espera",
    command=limpiar_cola_notificaciones
)

boton_limpiar.pack(pady=10)


# Información F9

ayuda = tk.Label(
    ventana,
    text="F9 → Mostrar / esconder interfaz"
)

ayuda.pack(pady=20)


# --------------------------------
# F9 GLOBAL
# --------------------------------

keyboard.add_hotkey(
    "f9",
    lambda: ventana.after(0, alternar_ui)
)


# --------------------------------
# INICIAR
# --------------------------------

# Mostrar la UI al iniciar
ventana.deiconify()
ventana.lift()

# Comprobar actualizaciones después de iniciar
ventana.after(
    100,
    comprobar_version
)

ventana.mainloop()