import os
import shutil
from Dominio.proyecto import Proyecto
from Infraestructura.repositorios_dao import RepositoriosDAO

class ServicioProyectos:
    def __init__(self):
        self.dao = RepositoriosDAO()
        # Ruta base física donde se alojarán las carpetas de los repos
        self.ruta_base = os.path.expanduser("~/.minigit")

    def crear_proyecto(self, id_usuario, nombre, descripcion, ruta, visibilidad):
        """Crea la carpeta física y hace el INSERT en la tabla."""
        #ruta_proyecto = os.path.join(self.ruta_base, nombre)
        ruta_proyecto = os.path.join(ruta, nombre)
        
        # 1. Crear carpeta física
        if not os.path.exists(ruta_proyecto):
            os.makedirs(ruta_proyecto)
            #print(f"Carpeta física creada: {ruta_proyecto}")
        else:
            raise Exception("Ya existe una carpeta con ese nombre en el servidor local.")

        # 2. Hacer INSERT en BD
        id_proyecto = self.dao.insertar_proyecto(id_usuario, nombre, descripcion, ruta, visibilidad)
        if id_proyecto:
            fecha_creacion = self.dao.obtener_fecha_creacion(id_proyecto)
            return Proyecto(id_proyecto, id_usuario, nombre, descripcion, ruta, visibilidad, fecha_creacion)
        raise Exception("Fallo en base de datos al registrar proyecto.")

    def listar_proyectos_usuario(self, id_usuario):
        """Hace un SELECT de proyectos del usuario."""
        return self.dao.obtener_proyectos_por_usuario(id_usuario)

    def eliminar_proyecto(self, id_proyecto):
        """Elimina carpeta física y hace DELETE en BD."""
        proyecto = self.dao.obtener_proyecto_por_id(id_proyecto)
        
        if proyecto:
            # 1. Eliminar carpeta física
            ruta_proyecto = os.path.join(proyecto.ruta, proyecto.nombre)
            if os.path.exists(ruta_proyecto):
                shutil.rmtree(ruta_proyecto)
                #print(f"Se eliminó el directorio físico: {ruta_proyecto}")
                
        # 2. Eliminar de la BD
        return self.dao.eliminar_proyecto(id_proyecto) is not None

    def detectar_lenguaje_proyecto(self, id_proyecto, ruta_proyecto=None):
        """Detecta automáticamente el lenguaje predominante del proyecto según extensiones."""
        archivos = self.dao.obtener_archivos_por_proyecto(id_proyecto)
        ext_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
            '.html': 'HTML', '.css': 'CSS', '.java': 'Java',
            '.cpp': 'C++', '.c': 'C', '.cs': 'C#', '.php': 'PHP',
            '.sql': 'SQL', '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust',
            '.jsx': 'JavaScript'
        }
        conteo = {}
        for a in archivos:
            nombre = getattr(a, 'nombre', '')
            ext = str(os.path.splitext(nombre)[1].lower())
            if ext in ext_map:
                lang = ext_map[ext]
                conteo[lang] = conteo.get(lang, 0) + 1

        if conteo:
            return max(conteo, key=conteo.get)

        # Si no hay archivos en BD pero existe la ruta física, escanearla
        if not conteo and ruta_proyecto and os.path.exists(ruta_proyecto):
            try:
                for f in os.listdir(ruta_proyecto):
                    ext = os.path.splitext(f)[1].lower()
                    if ext in ext_map:
                        lang = ext_map[ext]
                        conteo[lang] = conteo.get(lang, 0) + 1
            except Exception:
                pass
        
        if conteo:
            return max(conteo, key=conteo.get)

        return "General"