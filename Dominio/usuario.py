class Usuario:
    """Modelo de dominio para los usuarios del sistema."""
    def __init__(self, id, nombre, correo, password_hash, estado="Activo"):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.password_hash = password_hash
        self.estado = estado