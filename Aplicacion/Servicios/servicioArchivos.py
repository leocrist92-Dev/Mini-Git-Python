import os
import shutil
from Dominio.archivo import Archivo
from Dominio.tipo_archivo import TipoArchivo
from Infraestructura.repositorios_dao import RepositoriosDAO

class ServicioArchivos:
    def __init__(self):
        self.dao = RepositoriosDAO()
        self.ruta_base = os.path.expanduser("~/.minigit")

    def agregar_archivos_a_proyecto(self, id_proyecto, lista_rutas):
        """Copia archivos del PC del usuario a la carpeta del proyecto y hace el INSERT."""
        proyecto = self.dao.obtener_proyecto_por_id(id_proyecto)
        if not proyecto:
            raise Exception("Proyecto no encontrado.")
            
        ruta_destino_proyecto = os.path.join(self.ruta_base, proyecto.nombre)
        archivos_creados = []
        
        for ruta_origen in lista_rutas:
            if not os.path.exists(ruta_origen):
                continue
                
            nombre_archivo = os.path.basename(ruta_origen)
            ruta_final = os.path.join(ruta_destino_proyecto, nombre_archivo)
            
            # 1. Copia física
            try:
                shutil.copy(ruta_origen, ruta_final)
                print(f"Copiado {nombre_archivo} a {ruta_destino_proyecto}")
            except Exception as e:
                print(f"Fallo copiando {nombre_archivo}: {e}")
                continue
            
            # 2. Registrar en la BD (Id_tipo genérico = 1 para este flujo)
            id_archivo = self.dao.insertar_archivo(id_proyecto, 1, nombre_archivo)
            if id_archivo:
                archivos_creados.append(Archivo(id_archivo, id_proyecto, 1, nombre_archivo))
                
        return archivos_creados

    def obtener_archivos_proyecto(self, id_proyecto):
        """Lista archivos actuales de la vista."""
        return self.dao.obtener_archivos_por_proyecto(id_proyecto)