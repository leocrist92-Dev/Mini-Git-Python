class Proyecto:
    """Modelo de dominio para los repositorios/proyectos."""
    def __init__(self, id, id_usuario, nombre, descripcion, visibilidad, fecha_creacion=None):
        self.id = id
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.descripcion = descripcion
        self.visibilidad = visibilidad
        self.fecha_creacion = fecha_creacion