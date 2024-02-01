#pip install pywin32
#pip install sqlite3

import sqlite3
import os
import sys
import ctypes
import winreg as reg
import subprocess
from datetime import datetime

def set_reg_key():
    try:
        key = r"Software\Microsoft\Windows\CurrentVersion\Run"
        value_name = "RegistroAutomatico"
        script_path = os.path.abspath(__file__)

        key_handle = reg.OpenKey(reg.HKEY_CURRENT_USER, key, 0, reg.KEY_SET_VALUE)
        reg.SetValueEx(key_handle, value_name, 0, reg.REG_SZ, script_path)
        reg.CloseKey(key_handle)

    except Exception as e:
        print(f"Error al configurar la clave del registro: {e}")

# Verificar si el script se está ejecutando como administrador en Windows
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect('registro_usuarios_procesos.db')

# Crear un cursor para ejecutar consultas SQL
cursor = conn.cursor()

# Crear tabla de usuarios si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        email TEXT
    )
''')

# Crear tabla de procesos si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS procesos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        descripcion TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
    )
''')

# Función para registrar un nuevo usuario
def registrar_usuario(nombre, email):
    cursor.execute('''
        INSERT INTO usuarios (nombre, email)
        VALUES (?, ?)
    ''', (nombre, email))
    conn.commit()
    print(f'Usuario registrado: {nombre}')

# Función para registrar un nuevo proceso asociado a un usuario
def registrar_proceso(usuario_id, descripcion):
    cursor.execute('''
        INSERT INTO procesos (usuario_id, descripcion)
        VALUES (?, ?)
    ''', (usuario_id, descripcion))
    conn.commit()
    print(f'Proceso registrado para el usuario ID {usuario_id}: {descripcion}')

# Ejemplo de uso
registrar_usuario('Usuario1', 'usuario1@email.com')
registrar_usuario('Usuario2', 'usuario2@email.com')

registrar_proceso(1, 'Proceso A')
registrar_proceso(2, 'Proceso B')

# Cerrar la conexión a la base de datos al finalizar
conn.close()

if is_admin():
    set_reg_key()
else:
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
