class Archivo:
    """Representa un archivo rastreado dentro de un proyecto."""
    def __init__(self, id, id_proyecto, id_tipo, nombre, fecha_creacion=None):
        self.id = id
        self.id_proyecto = id_proyecto
        self.id_tipo = id_tipo
        self.nombre = nombre
        self.fecha_creacion = fecha_creacion