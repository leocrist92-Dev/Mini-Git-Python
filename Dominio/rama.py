class Rama:
    """Representa una ramificación en la línea de tiempo del proyecto."""
    def __init__(self, id, id_proyecto, nombre, id_version_base, fecha_creacion, activa):
        self.id = id
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.id_version_base = id_version_base
        self.fecha_creacion = fecha_creacion
        self.activa = activa