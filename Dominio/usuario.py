class Usuario:
    """Modelo de dominio para los usuarios del sistema."""
    def __init__(self, id, nombre, correo, nombre_usuario, password_hash, rol=None, estado="Activo"):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.nombre_usuario = nombre_usuario
        self.password_hash = password_hash
        self.rol = rol
        self.estado = estado