import os
import shutil
from Dominio.proyecto import Proyecto
from Infraestructura.repositorios_dao import RepositoriosDAO

class ServicioProyectos:
    def __init__(self):
        self.dao = RepositoriosDAO()
        # Ruta base física donde se alojarán las carpetas de los repos
        self.ruta_base = os.path.expanduser("~/.minigit")

    def crear_proyecto(self, id_usuario, nombre, descripcion, visibilidad):
        """Crea la carpeta física y hace el INSERT en la tabla."""
        ruta_proyecto = os.path.join(self.ruta_base, nombre)
        
        # 1. Crear carpeta física
        if not os.path.exists(ruta_proyecto):
            os.makedirs(ruta_proyecto)
            print(f"Carpeta física creada: {ruta_proyecto}")
        else:
            raise Exception("Ya existe una carpeta con ese nombre en el servidor local.")

        # 2. Hacer INSERT en BD
        id_proyecto = self.dao.insertar_proyecto(id_usuario, nombre, descripcion, visibilidad)
        if id_proyecto:
            return Proyecto(id_proyecto, id_usuario, nombre, descripcion, visibilidad)
        raise Exception("Fallo en base de datos al registrar proyecto.")

    def listar_proyectos_usuario(self, id_usuario):
        """Hace un SELECT de proyectos del usuario."""
        return self.dao.obtener_proyectos_por_usuario(id_usuario)

    def eliminar_proyecto(self, id_proyecto):
        """Elimina carpeta física y hace DELETE en BD."""
        proyecto = self.dao.obtener_proyecto_por_id(id_proyecto)
        
        if proyecto:
            # 1. Eliminar carpeta física
            ruta_proyecto = os.path.join(self.ruta_base, proyecto.nombre)
            if os.path.exists(ruta_proyecto):
                shutil.rmtree(ruta_proyecto)
                print(f"Se eliminó el directorio físico: {ruta_proyecto}")
                
        # 2. Eliminar de la BD
        return self.dao.eliminar_proyecto(id_proyecto) is not None