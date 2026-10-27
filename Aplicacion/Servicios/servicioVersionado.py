import hashlib
import zipfile
import os
import datetime
import shutil
import difflib
from Dominio.version_archivo import VersionArchivo
from Dominio.rama import Rama
from Infraestructura.repositorios_dao import RepositoriosDAO

class ServicioVersionado:
    """Clase principal (la más importante) que maneja los commits, ramas y restauraciones."""
    
    def __init__(self):
        self.dao = RepositoriosDAO()
        self.ruta_base = os.path.expanduser("~/.minigit")

    def normalizar_texto(self, texto):
        """Normaliza los saltos de línea para evitar falsas diferencias entre Windows y Unix."""
        if texto is None: return None
        return texto.replace('\r\n', '\n')

    def obtener_historial(self, id_proyecto):
        """Hace SELECT ordenado por fecha desc."""
        return self.dao.obtener_versiones_proyecto_desc(id_proyecto)

    def contar_commits_totales_usuario(self, id_usuario):
        """Obtiene la suma global de commits de todos los proyectos del usuario."""
        return self.dao.contar_commits_totales_usuario(id_usuario)

    def obtener_ultima_actualizacion(self, id_proyecto, fecha_creacion_defecto=None):
        """Retorna la fecha del ultimo commit o la fecha de creacion si no hay commits."""
        ultima_fecha = self.dao.obtener_ultima_fecha_commit(id_proyecto)
        if ultima_fecha:
            return ultima_fecha
        return fecha_creacion_defecto

    

    def crear_rama(self, id_proyecto, nombre_rama, id_version_base=None, activa='No'):
        """
        Crea una nueva rama validando que no existan duplicados.
        Permite activarla directamente si el flag 'activa' es True.
        """
        if not nombre_rama or not nombre_rama.strip():
            raise Exception("El nombre de la rama es obligatorio.")

        nombre_clean = nombre_rama.strip()

        # Validación de duplicado
        ramas_existentes = self.obtener_ramas_proyecto(id_proyecto)
        for r in ramas_existentes:
            r_nombre = r.get('nombre') if isinstance(r, dict) else getattr(r, 'nombre', '')
            if r_nombre.lower() == nombre_clean.lower():
                raise Exception(f"Ya existe una rama con el nombre '{nombre_clean}' en este proyecto.")
            
        id_rama = self.dao.crear_rama(id_proyecto, nombre_rama, id_version_base, activa)
        if id_rama:
            return Rama(id_rama, id_proyecto, nombre_rama, id_version_base, None, activa)
        raise Exception("Error al generar la rama en BD.")

    def obtener_rama_activa(self, id_proyecto):
        return self.dao.obtener_rama_activa(id_proyecto)

    def cambiar_rama_activa(self, id_proyecto, id_rama):
        """
        Cambia la rama activa del proyecto.
        """
        if not id_proyecto or not id_rama:
            raise Exception("Parámetros no válidos para cambiar la rama activa.")
        return self.dao.cambiar_rama_activa(id_proyecto, id_rama)

    def obtener_ramas_proyecto(self, id_proyecto):
        """
        Consulta las ramas asociadas a un proyecto específico.
        """
        if not self.dao:
            return []
        return self.dao.obtener_ramas_proyecto(id_proyecto)

    def restaurar_version(self, id_proyecto, id_version):
        """Sobrescribe archivos físicos con los del backup de ese commit."""
        # Se requiere extraer el zip de la versión seleccionada y sobrescribir
        print(f"Extrayendo y sobrescribiendo archivos físicos al estado del commit {id_version}...")
        return True

    #para commit de todos los archivos
    def obtener_contenido_ultimo_commit(self, id_archivo, ruta_zip):
        if not ruta_zip or not os.path.exists(ruta_zip):
            return None
        try:
            with zipfile.ZipFile(ruta_zip, 'r') as zf:
                archivos = zf.namelist()
                if archivos:
                    with zf.open(archivos[0]) as f:
                        raw = f.read().decode('utf-8', errors='replace')
                        return self.normalizar_texto(raw)
        except Exception as e:
            print(f"Error leyendo zip de commit anterior: {e}")
        return None

    def escanean_y_calcular_diferencias(self, id_proyecto, ruta_proyecto):
        if not ruta_proyecto or not os.path.exists(ruta_proyecto):
            return {"cambios": [], "diff_texto": "Ruta física del proyecto no encontrada."}

        cambios = []
        lineas_diff_totales = []

        # Recorrer archivos físicos en la carpeta del repositorio
        for root, dirs, files in os.walk(ruta_proyecto):
            # Ignorar carpetas ocultas o de sistema
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files:
                if file.startswith('.'): continue
                
                ruta_abs = os.path.join(root, file)
                rel_path = os.path.relpath(ruta_abs, ruta_proyecto)

                # Leer contenido en disco
                try:
                    with open(ruta_abs, 'r', encoding='utf-8', errors='replace') as f:
                        contenido_actual = f.read()
                except Exception:
                    continue

                # Buscar si existe versión previa en BD
                id_archivo = self.dao.obtener_o_crear_archivo(id_proyecto, file, rel_path)
                version_previa = self.dao.obtener_ultima_version_archivo(id_archivo)
                
                contenido_anterior = None
                if version_previa:
                    contenido_anterior = self.obtener_contenido_ultimo_commit(id_archivo, version_previa.contenido_comprimido)

                # Si el contenido actual es exactamente igual al anterior, NO hay cambios
                if contenido_anterior is not None and contenido_actual == contenido_anterior:
                    continue

                # Si es un archivo nuevo sin versión previa
                if contenido_anterior is None:
                    lineas_ant = []
                    # Archivo completamente nuevo
                    lineas_act = contenido_actual.splitlines(keepends=True)
                    diff = [f"--- a/{file}\n", f"+++ b/{file}\n", f"@@ -0,0 +1,{len(lineas_act)} @@\n"]
                    diff.extend([f"+{line if line.endswith('\n') else line + '\n'}" for line in lineas_act])
                else:
                    # Archivo modificado
                    lineas_ant = contenido_anterior.splitlines(keepends=True)
                    lineas_ant[-1] += "\n"
                    lineas_act = contenido_actual.splitlines(keepends=True)
                    lineas_act[-1] += "\n\n"
                    diff = list(difflib.unified_diff(
                        lineas_ant,
                        lineas_act,
                        fromfile=f"a/{file}",
                        tofile=f"b/{file}"
                    ))

                # Calcular Diff con difflib
                diff = list(difflib.unified_diff(
                    lineas_ant,
                    lineas_act,
                    fromfile=f"a/{file}",
                    tofile=f"b/{file}"
                ))

                    
                if diff:
                    cambios.append({
                        "id_archivo": id_archivo,
                        "nombre": file,
                        "ruta_relativa": rel_path,
                        "ruta_abs": ruta_abs,
                        "es_nuevo": contenido_anterior is None
                    })
                    lineas_diff_totales.extend(diff)
                    lineas_diff_totales.append("\n") # Espacio entre archivos

        diff_texto = "".join(lineas_diff_totales) if lineas_diff_totales else "No se detectaron cambios en los archivos del proyecto."
        return {"cambios": cambios, "diff_texto": diff_texto}

    def crear_commit_completo(self, id_proyecto, id_usuario, lista_archivos, mensaje, descripcion, diff_texto):
        if not mensaje.strip():
            raise Exception("El mensaje de commit es obligatorio.")
        if not lista_archivos:
            raise Exception("No hay archivos seleccionados para hacer commit.")

        rama_obj = self.dao.obtener_rama_activa(id_proyecto)
        id_rama = rama_obj.id

        proyecto = self.dao.obtener_proyecto_por_id(id_proyecto)
        if not proyecto: raise Exception("Proyecto no válido.")

        ruta_completa = os.path.join(proyecto.ruta, proyecto.nombre)
        
        carpeta_commits = os.path.join(ruta_completa, ".commits")
        if not os.path.exists(carpeta_commits):
            os.makedirs(carpeta_commits)

        versiones_creadas = []
        # 1. Generar un Hash único global para el Commit
        timestamp = datetime.datetime.now().isoformat()
        cadena_commit = f"{id_proyecto}-{id_usuario}-{timestamp}-{mensaje}"
        hash_commit = hashlib.sha1(cadena_commit.encode('utf-8')).hexdigest()

        # 2. Archivo ZIP único para todo el commit
        ruta_zip = os.path.join(carpeta_commits, f"{hash_commit}.zip")

        with zipfile.ZipFile(ruta_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Empaquetar cada archivo modificado/nuevo en el ZIP
            for item in lista_archivos:
                ruta_abs = item['ruta_abs']
                if os.path.exists(ruta_abs):
                    arc_name = item.get('ruta_relativa', item['nombre'])
                    zf.write(ruta_abs, arcname=arc_name)

            # Empaquetar el diff dentro de la carpeta virtual 'diff/diff.txt'
            if diff_texto:
                zf.writestr('diff/diff.txt', diff_texto)

        # 3. Insertar única cabecera del commit en la tabla 'etiqueta'
        id_etiqueta = self.dao.insertar_etiqueta(
            id_usuario, hash_commit, mensaje, descripcion, ruta_zip, id_rama
        )

        if not id_etiqueta:
            raise Exception("Error al insertar el registro de commit en la tabla 'etiqueta'.")

        # 4. Registrar la relación en 'versiones_archivos' para cada archivo
        archivos_guardados = 0
        for item in lista_archivos:
            res = self.dao.insertar_version_archivo(item['id_archivo'], id_etiqueta)
            if res:
                archivos_guardados += 1

        return archivos_guardados > 0

    def obtener_historial_proyecto(self, id_proyecto):
        return self.dao.obtener_historial_commits_proyecto(id_proyecto)

    # --- MOTOR DE COMPARACIÓN DE VERSIONES (DIFF) ---
    def _extraer_archivos_de_zip(self, ruta_zip):
        """
        Extrae y decodifica todos los archivos de código guardados en un ZIP de commit.
        """
        archivos = {}
        if ruta_zip and os.path.exists(ruta_zip):
            try:
                with zipfile.ZipFile(ruta_zip, 'r') as zf:
                    for nombre in zf.namelist():
                        if not nombre.startswith("diff/"):
                            contenido = zf.read(nombre).decode('utf-8', errors='replace')
                            archivos[nombre] = contenido
            except Exception as e:
                print(f"Error leyendo paquete ZIP ({ruta_zip}): {e}")
        return archivos

    def comparar_versiones(self, id_etiqueta_a, id_etiqueta_b):
        """
        Compara dos versiones (commits) completas del proyecto.
        Retorna una estructura con:
        - raw_unified_diff: Texto plano en formato Unified Diff para la vista unificada.
        - side_by_side: Estructura formateada línea por línea para la vista de dos paneles.
        - stats: Métricas numéricas globales (archivos cambiados, adiciones, eliminaciones).
        """
        etiqueta_a = self.dao.obtener_etiqueta_por_id(id_etiqueta_a)
        etiqueta_b = self.dao.obtener_etiqueta_por_id(id_etiqueta_b)

        if not etiqueta_a or not etiqueta_b:
            raise Exception("Una de las versiones seleccionadas no fue encontrada.")

        archivos_a = self._extraer_archivos_de_zip(etiqueta_a['contenido_comprimido'])
        archivos_b = self._extraer_archivos_de_zip(etiqueta_b['contenido_comprimido'])

        todos_los_archivos = sorted(list(set(archivos_a.keys()) | set(archivos_b.keys())))

        unified_lines = []
        archivos_detalle = []

        total_adiciones = 0
        total_eliminaciones = 0
        archivos_modificados_cnt = 0
        archivos_nuevos_cnt = 0
        archivos_eliminados_cnt = 0

        for nombre_archivo in todos_los_archivos:
            en_a = nombre_archivo in archivos_a
            en_b = nombre_archivo in archivos_b

            text_a = archivos_a.get(nombre_archivo, "")
            text_b = archivos_b.get(nombre_archivo, "")

            lines_a = text_a.splitlines()
            lines_b = text_b.splitlines()

            if text_a == text_b:
                continue

            archivos_modificados_cnt += 1
            if not en_a and en_b:
                estado = "nuevo"
                archivos_nuevos_cnt += 1
            elif en_a and not en_b:
                estado = "eliminado"
                archivos_eliminados_cnt += 1
            else:
                estado = "modificado"

            # 1. Generar Unified Diff
            diff_file_lines = list(difflib.unified_diff(
                [l + '\n' for l in lines_a],
                [l + '\n' for l in lines_b],
                fromfile=f"a/{nombre_archivo}",
                tofile=f"b/{nombre_archivo}"
            ))
            unified_lines.extend(diff_file_lines)
            unified_lines.append("\n") # Espacio entre archivos

            # 2. Generar Diff Lado a Lado (Side-by-Side)
            matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
            side_by_side_lines = []
            file_add = 0
            file_sub = 0

            idx_a, idx_b = 1, 1
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                if tag == 'equal':
                    for la, lb in zip(lines_a[i1:i2], lines_b[j1:j2]):
                        side_by_side_lines.append((str(idx_a), la, 'normal', str(idx_b), lb, 'normal'))
                        idx_a += 1
                        idx_b += 1
                elif tag == 'replace':
                    len1 = i2 - i1
                    len2 = j2 - j1
                    for k in range(max(len1, len2)):
                        num_a = str(idx_a) if k < len1 else ""
                        val_a = lines_a[i1 + k] if k < len1 else ""
                        st_a = 'modified' if k < len1 else 'empty'
                        if k < len1:
                            idx_a += 1
                            file_sub += 1

                        num_b = str(idx_b) if k < len2 else ""
                        val_b = lines_b[j1 + k] if k < len2 else ""
                        st_b = 'modified' if k < len2 else 'empty'
                        if k < len2:
                            idx_b += 1
                            file_add += 1

                        side_by_side_lines.append((num_a, val_a, st_a, num_b, val_b, st_b))
                elif tag == 'delete':
                    for la in lines_a[i1:i2]:
                        side_by_side_lines.append((str(idx_a), la, 'deleted', "", "", 'empty'))
                        idx_a += 1
                        file_sub += 1
                elif tag == 'insert':
                    for lb in lines_b[j1:j2]:
                        side_by_side_lines.append(("", "", 'empty', str(idx_b), lb, 'added'))
                        idx_b += 1
                        file_add += 1

            total_adiciones += file_add
            total_eliminaciones += file_sub

            archivos_detalle.append({
                "nombre": nombre_archivo,
                "estado": estado,
                "adiciones": file_add,
                "eliminaciones": file_sub,
                "side_by_side": side_by_side_lines
            })

        return {
            "raw_unified_diff": "".join(unified_lines),
            "archivos_detalle": archivos_detalle,
            "stats": {
                "archivos_modificados": archivos_modificados_cnt,
                "archivos_nuevos": archivos_nuevos_cnt,
                "archivos_eliminados": archivos_eliminados_cnt,
                "adiciones": total_adiciones,
                "eliminaciones": total_eliminaciones,
                "commit_a": etiqueta_a,
                "commit_b": etiqueta_b
            }
        }

    def resolver_ruta_zip_valida(self, id_proyecto, ruta_zip_db, hash_version=None):
        """
        Resuelve de forma dinámica la ruta física de un archivo ZIP de commit.
        Soporta rutas corruptas por codificación (tildes), barras mezcladas o proyectos movidos de carpeta.
        """
        if not ruta_zip_db and not hash_version:
            return None

        # 1. Probar la ruta guardada en BD normalizada
        if ruta_zip_db:
            ruta_norm = os.path.normpath(ruta_zip_db)
            if os.path.exists(ruta_norm):
                return ruta_norm

        # 2. Si la ruta directa no existe, intentar reconstruirla dinámicamente desde el proyecto
        if id_proyecto and self.dao and hasattr(self.dao, 'obtener_proyecto_por_id'):
            try:
                proyecto = self.dao.obtener_proyecto_por_id(id_proyecto)
                if proyecto:
                    nombre_zip = os.path.basename(ruta_zip_db) if ruta_zip_db else f"{hash_version}.zip"
                    
                    # Rutas posibles donde puede residir la carpeta .commits
                    p_ruta = os.path.normpath(proyecto.ruta)
                    candidatos = [
                        os.path.join(p_ruta, proyecto.nombre, ".commits", nombre_zip),
                        os.path.join(p_ruta, ".commits", nombre_zip),
                    ]

                    for cand in candidatos:
                        cand_norm = os.path.normpath(cand)
                        if os.path.exists(cand_norm):
                            return cand_norm
            except Exception as e:
                print(f"Error al resolver la ruta dinámica del ZIP: {e}")

        return None