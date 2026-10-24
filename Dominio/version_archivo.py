class VersionArchivo:
    """Representa un 'Commit' en el sistema."""
    def __init__(self, id, id_archivo, id_usuario, hash_version, mensaje, descripcion=None, contenido_comprimido=None, fecha=None, rama=None):
        self.id = id
        self.id_archivo = id_archivo
        self.id_usuario = id_usuario
        self.hash_version = hash_version
        self.mensaje = mensaje
        self.descripcion = descripcion
        self.contenido_comprimido = contenido_comprimido
        self.fecha = fecha
        self.rama = rama