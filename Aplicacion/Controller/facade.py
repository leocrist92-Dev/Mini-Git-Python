from Aplicacion.Servicios.servicioUsuarios import ServicioUsuarios
from Aplicacion.Servicios.servicioProyectos import ServicioProyectos
from Aplicacion.Servicios.servicioArchivos import ServicioArchivos
from Aplicacion.Servicios.servicioVersionado import ServicioVersionado
from Aplicacion.Servicios.servicioEtiquetas import ServicioEtiquetas

class MiniGitFacade:
    """
    Punto de entrada único.
    Patrón estructural que oculta la complejidad del backend a las interfaces visuales.
    """
    def __init__(self):
        self.srv_usuarios = ServicioUsuarios()
        self.srv_proyectos = ServicioProyectos()
        self.srv_archivos = ServicioArchivos()
        self.srv_versionado = ServicioVersionado()
        self.srv_etiquetas = ServicioEtiquetas()

    # --- Puntos de Acceso UI : Usuarios ---
    def autenticar(self, correo, password):
        return self.srv_usuarios.autenticar(correo, password)

    def registrar(self, nombre, correo, usuario, password):
        return self.srv_usuarios.registrar(nombre, correo, usuario, password)

    def listar_usuarios(self):
        return self.srv_usuarios.listar_usuarios()

    def cambiar_estado_usuario(self, id_usuario, estado):
        return self.srv_usuarios.cambiar_estado_usuario(id_usuario, estado)

    # --- Puntos de Acceso UI : Proyectos ---
    def crear_proyecto(self, id_usuario, nombre, descripcion, ruta, visibilidad):
        return self.srv_proyectos.crear_proyecto(id_usuario, nombre, descripcion, ruta, visibilidad)

    def listar_proyectos_usuario(self, id_usuario):
        return self.srv_proyectos.listar_proyectos_usuario(id_usuario)

    def eliminar_proyecto(self, id_proyecto):
        return self.srv_proyectos.eliminar_proyecto(id_proyecto)

    # --- Puntos de Acceso UI : Archivos ---
    def agregar_archivos_a_proyecto(self, id_proyecto, lista_rutas):
        return self.srv_archivos.agregar_archivos_a_proyecto(id_proyecto, lista_rutas)

    def obtener_archivos_proyecto(self, id_proyecto):
        return self.srv_archivos.obtener_archivos_proyecto(id_proyecto)

    # --- Puntos de Acceso UI : Versionado ---
    def crear_commit(self, id_proyecto, id_usuario, archivos_seleccionados, mensaje):
        return self.srv_versionado.crear_commit(id_proyecto, id_usuario, archivos_seleccionados, mensaje)

    def obtener_historial(self, id_proyecto):
        return self.srv_versionado.obtener_historial(id_proyecto)

    def contar_commits_totales_usuario(self, id_usuario):
        return self.srv_versionado.contar_commits_totales_usuario(id_usuario)

    def obtener_ultima_actualizacion(self, id_proyecto, fecha_creacion_defecto=None):
        return self.srv_versionado.obtener_ultima_actualizacion(id_proyecto, fecha_creacion_defecto)

    def obtener_lenguaje_proyecto(self, id_proyecto, ruta_proyecto=None):
        return self.srv_proyectos.detectar_lenguaje_proyecto(id_proyecto, ruta_proyecto)

    def comparar_versiones(self, id_version1, id_version2):
        return self.srv_versionado.comparar_versiones(id_version1, id_version2)

    def crear_rama(self, id_proyecto, nombre_rama, id_version_base):
        return self.srv_versionado.crear_rama(id_proyecto, nombre_rama, id_version_base)

    def restaurar_version(self, id_proyecto, id_version):
        return self.srv_versionado.restaurar_version(id_proyecto, id_version)

    # --- Puntos de Acceso UI : Etiquetas ---
    def crear_etiqueta(self, id_proyecto, nombre, descripcion):
        return self.srv_etiquetas.crear_etiqueta(id_proyecto, nombre, descripcion)

    def asignar_etiqueta_a_version(self, id_version, id_etiqueta):
        return self.srv_etiquetas.asignar_etiqueta_a_version(id_version, id_etiqueta)

if __name__ == "__main__":
    print("Iniciando capa Facade de Mini-Git separada en módulos.")
    app = MiniGitFacade()
    print("Módulos cargados con éxito. La base de datos y la interfaz gráfica pueden comenzar a consumir las funciones.")