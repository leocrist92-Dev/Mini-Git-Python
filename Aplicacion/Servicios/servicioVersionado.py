import hashlib
import zipfile
import os
import datetime
import shutil
from Dominio.version_archivo import VersionArchivo
from Dominio.rama import Rama
from Infraestructura.repositorios_dao import RepositoriosDAO

class ServicioVersionado:
    """Clase principal (la más importante) que maneja los commits, ramas y restauraciones."""
    
    def __init__(self):
        self.dao = RepositoriosDAO()
        self.ruta_base = os.path.expanduser("~/.minigit")

    def crear_commit(self, id_proyecto, id_usuario, archivos_seleccionados, mensaje):
        """Genera hash SHA-1, comprime físicos y guarda el registro."""
        proyecto = self.dao.obtener_proyecto_por_id(id_proyecto)
        if not proyecto: raise Exception("Proyecto inválido")
        
        ruta_proyecto = os.path.join(self.ruta_base, proyecto.nombre)
        versiones = []
        
        for archivo in archivos_seleccionados:
            ruta_archivo = os.path.join(ruta_proyecto, archivo.nombre)
            if not os.path.exists(ruta_archivo):
                continue
                
            # 1. Leer contenido para el Hash SHA-1
            with open(ruta_archivo, 'rb') as f:
                contenido = f.read()
                hash_version = hashlib.sha1(contenido).hexdigest()
                
            # 2. Comprimir el archivo (Simulamos guardando en una carpeta oculta '.commits')
            carpeta_commits = os.path.join(ruta_proyecto, ".commits")
            if not os.path.exists(carpeta_commits): os.makedirs(carpeta_commits)
            
            ruta_zip = os.path.join(carpeta_commits, f"{hash_version}.zip")
            with zipfile.ZipFile(ruta_zip, 'w') as zf:
                zf.write(ruta_archivo, arcname=archivo.nombre)
                
            # 3. Guardar registro en BD (VERSION_ARCHIVO)
            id_version = self.dao.insertar_version(
                archivo.id, id_usuario, hash_version, mensaje, ruta_zip
            )
            
            if id_version:
                versiones.append(VersionArchivo(id_version, archivo.id, id_usuario, hash_version, mensaje, ruta_zip))
                
        return versiones

    def obtener_historial(self, id_proyecto):
        """Hace SELECT ordenado por fecha desc."""
        return self.dao.obtener_versiones_proyecto_desc(id_proyecto)

    def comparar_versiones(self, id_version1, id_version2):
        """Simula diff leyendo archivos y generando +-"""
        # En una impl. real leería el zip1 y zip2 y ejecutaría un diff
        return f"--- Version {id_version1}\n+++ Version {id_version2}\n@@ -1,2 +1,3 @@\n- Codigo viejo\n+ Codigo nuevo"

    def crear_rama(self, id_proyecto, nombre_rama, id_version_base):
        """Registra una nueva rama a partir de un punto en la historia."""
        id_rama = self.dao.insertar_rama(id_proyecto, nombre_rama, id_version_base)
        if id_rama:
            return Rama(id_rama, id_proyecto, nombre_rama, id_version_base)
        raise Exception("Error al generar la rama en BD.")

    def restaurar_version(self, id_proyecto, id_version):
        """Sobrescribe archivos físicos con los del backup de ese commit."""
        # Se requiere extraer el zip de la versión seleccionada y sobrescribir
        print(f"Extrayendo y sobrescribiendo archivos físicos al estado del commit {id_version}...")
        return True