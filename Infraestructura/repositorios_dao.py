import os

try:
    from mysql.connector import Error
except ImportError:
    mysql = None
    Error = Exception


from Dominio.usuario import Usuario
from Dominio.proyecto import Proyecto
from Dominio.archivo import Archivo
from Dominio.tipo_archivo import TipoArchivo
from Dominio.version_archivo import VersionArchivo
from Dominio.rama import Rama
from Dominio.etiqueta import Etiqueta
from Dominio.version_etiqueta import VersionEtiqueta
from Infraestructura.conexion_mysql import ConexionMySQL

class RepositoriosDAO:
    """Clase DAO que centraliza todas las consultas a la Base de Datos."""
    def __init__(self):
        self.db = ConexionMySQL()

    def _ejecutar(self, query, params=None, fetch=False):
        conn = self.db.conectar()
        if not conn: return [] if fetch else False
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            conn.commit()
            return cursor.lastrowid
        except Error as e:
            print(f"Error SQL: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                cursor.close()
                self.db.cerrar()

    # --- Usuarios ---
    def obtener_usuario_por_correo(self, correo):
        q = "SELECT * FROM usuarios WHERE correo = %s;"
        res = self._ejecutar(q, (correo,), fetch=True)
        if res:
            u = res[0]
            return Usuario(u['id'], u['nombre'], u['correo'], u['password_hash'], u['estado'])
        return None

    def insertar_usuario(self, nombre, correo, usuario, password_hash):
        q = "INSERT INTO usuarios (nombre, correo, nombre_usuario, password_hash) VALUES (%s, %s, %s, %s);"
        return self._ejecutar(q, (nombre, correo, usuario, password_hash))

    def obtener_todos_usuarios(self):
        q = "SELECT * FROM usuarios;"
        res = self._ejecutar(q, fetch=True)
        return [Usuario(u['id'], u['nombre'], u['correo'], u['password_hash'], u['estado']) for u in res]

    def actualizar_estado_usuario(self, id_usuario, estado):
        q = "UPDATE usuarios SET estado = %s WHERE id = %s;"
        return self._ejecutar(q, (estado, id_usuario))

    # --- Proyectos ---
    def insertar_proyecto(self, id_usuario, nombre, descripcion, visibilidad):
        q = "INSERT INTO proyectos (id_usuario, nombre, descripcion, visibilidad) VALUES (%s, %s, %s, %s);"
        return self._ejecutar(q, (id_usuario, nombre, descripcion, visibilidad))

    def obtener_proyectos_por_usuario(self, id_usuario):
        q = "SELECT * FROM proyectos WHERE id_usuario = %s;"
        res = self._ejecutar(q, (id_usuario,), fetch=True)
        return [Proyecto(p['id'], p['id_usuario'], p['nombre'], p['descripcion'], p['visibilidad'], p['fecha_creacion']) for p in res]

    def eliminar_proyecto(self, id_proyecto):
        """Elimina el repositorio permanentemente de la BD."""
        q = "DELETE FROM proyectos WHERE id = %s;"
        return self._ejecutar(q, (id_proyecto,))

    def obtener_proyecto_por_id(self, id_proyecto):
        q = "SELECT * FROM proyectos WHERE id = %s;"
        res = self._ejecutar(q, (id_proyecto,), fetch=True)
        if res:
            p = res[0]
            return Proyecto(p['id'], p['id_usuario'], p['nombre'], p['descripcion'], p['visibilidad'], p['fecha_creacion'])
        return None

    # --- Archivos ---
    def insertar_archivo(self, id_proyecto, id_tipo, nombre):
        q = "INSERT INTO archivos (id_proyecto, id_tipo, nombre) VALUES (%s, %s, %s);"
        return self._ejecutar(q, (id_proyecto, id_tipo, nombre))

    def obtener_archivos_por_proyecto(self, id_proyecto):
        q = "SELECT * FROM archivos WHERE id_proyecto = %s;"
        res = self._ejecutar(q, (id_proyecto,), fetch=True)
        return [Archivo(a['id'], a['id_proyecto'], a['id_tipo'], a['nombre'], a['fecha_creacion']) for a in res]

    # --- Versionado (Commits y Ramas) ---
    def insertar_version(self, id_archivo, id_usuario, hash_version, mensaje, contenido_comprimido):
        q = """INSERT INTO versiones_archivo 
               (id_archivo, id_usuario, hash_version, mensaje, contenido_comprimido) 
               VALUES (%s, %s, %s, %s, %s);"""
        return self._ejecutar(q, (id_archivo, id_usuario, hash_version, mensaje, contenido_comprimido))

    def obtener_versiones_proyecto_desc(self, id_proyecto):
        # Se solicita ORDER BY fecha DESC
        q = """
            SELECT v.* FROM versiones_archivo v
            JOIN archivos a ON v.id_archivo = a.id
            WHERE a.id_proyecto = %s 
            ORDER BY v.fecha DESC;
        """
        res = self._ejecutar(q, (id_proyecto,), fetch=True)
        return [VersionArchivo(v['id'], v['id_archivo'], v['id_usuario'], v['hash_version'], v['mensaje'], v['contenido_comprimido'], v['fecha']) for v in res]

    def insertar_rama(self, id_proyecto, nombre, id_version_base):
        q = "INSERT INTO ramas (id_proyecto, nombre, id_version_base) VALUES (%s, %s, %s);"
        return self._ejecutar(q, (id_proyecto, nombre, id_version_base))

    # --- Etiquetas ---
    def insertar_etiqueta(self, id_proyecto, nombre, descripcion):
        q = "INSERT INTO etiquetas (id_proyecto, nombre, descripcion) VALUES (%s, %s, %s);"
        return self._ejecutar(q, (id_proyecto, nombre, descripcion))

    def insertar_version_etiqueta(self, id_version, id_etiqueta):
        q = "INSERT INTO versiones_etiquetas (id_version, id_etiqueta) VALUES (%s, %s);"
        return self._ejecutar(q, (id_version, id_etiqueta))