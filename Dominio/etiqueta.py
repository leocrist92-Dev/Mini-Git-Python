class Etiqueta:
    """Tags o releases asignados a commits específicos."""
    def __init__(self, id, id_proyecto, nombre, descripcion):
        self.id = id
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion