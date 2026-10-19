from Dominio.etiqueta import Etiqueta
from Infraestructura.repositorios_dao import RepositoriosDAO

class ServicioEtiquetas:
    """Maneja las versiones (Tags/Releases) de los proyectos."""
    def __init__(self):
        self.dao = RepositoriosDAO()

    def crear_etiqueta(self, id_proyecto, nombre, descripcion):
        """Registra una nueva etiqueta."""
        id_etiqueta = self.dao.insertar_etiqueta(id_proyecto, nombre, descripcion)
        if id_etiqueta:
            return Etiqueta(id_etiqueta, id_proyecto, nombre, descripcion)
        raise Exception("Ocurrió un problema guardando la etiqueta en base de datos.")

    def asignar_etiqueta_a_version(self, id_version, id_etiqueta):
        """Asigna una etiqueta registrada a un Commit existente."""
        return self.dao.insertar_version_etiqueta(id_version, id_etiqueta) is not None