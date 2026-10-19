import os

try:
    import mysql.connector
    from mysql.connector import Error
except ImportError:
    mysql = None
    Error = Exception

#from modelos import Usuario, Proyecto, Archivo, VersionArchivo

class ConexionMySQL:
    """Maneja la conexión a la base de datos MySQL."""
    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = ""
        self.database = "minigit_db"
        self.conexion = None

    def conectar(self):
        if mysql is None:
            print("AVISO: mysql-connector-python no instalado. Modo simulador activo.")
            return None
        try:
            self.conexion = mysql.connector.connect(
                host=self.host, user=self.user,
                password=self.password, database=self.database
            )
            return self.conexion
        except Error as e:
            print(f"Error al conectar a la BD: {e}")
            return None

    def cerrar(self):
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()