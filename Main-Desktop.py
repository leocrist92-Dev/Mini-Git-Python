import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from Aplicacion.Controller.facade import MiniGitFacade
from Dominio.proyecto import Proyecto

import os
import sys
import datetime
import hashlib
import zipfile
import difflib
import shutil


class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mini-Git | Análisis y Desarrollo (ADSO)")
        self.geometry("1000x700")
        
        # Paleta de colores exacta de theme.css
        self.colors = {
            "bg": "#070b17",
            "panel": "#0f172a",
            "panel_2": "#101a33",
            "text": "#e5ecff",
            "muted": "#9aa7c7",
            "blue": "#2563ff",
            "purple": "#8b5cf6",
            "red": "#ef4444",
            "cyan": "#38bdf8",
            "ok": "#22c55e",
            "warn": "#f59e0b",
            "border": "#1e293b", # Aproximación a rgba(255,255,255,.14)
            "fg": "#ffffff"
        }
        
        self.configure(bg=self.colors["bg"])
        self.eval('tk::PlaceWindow . center')

        # Instanciación Dinámica de la Fachada Real
        self.facade = MiniGitFacade()

        # Estado Global de Sesión y Contexto de Aplicación
        self.usuario_actual = None
        self.proyecto_actual = None
        
        self.setup_styles()
        
        # Contenedor principal
        self.container = ttk.Frame(self, style='App.TFrame')
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        # Inicializando vistas
        for F in (HU001_Login, HU002_Registro, HU009_ListarRepositorios, HU003_CrearRepo, 
                  HU004_Commit, HU005_Historial, HU006_Diff, HU007_Ramas, HU008_Merge, HU010_EliminarRepo):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("HU001_Login")

    def set_usuario_actual(self, usuario):
            self.usuario_actual = usuario
    
    def set_proyecto_actual(self, proyecto):
            self.proyecto_actual = proyecto

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frames
        style.configure('App.TFrame', background=self.colors["bg"])
        style.configure('Panel.TFrame', background=self.colors["panel"])
        style.configure('Panel2.TFrame', background=self.colors["panel_2"])
        
        # LabelFrames
        style.configure('TLabelFrame', background=self.colors["panel"], bordercolor=self.colors["border"])
        style.configure('TLabelFrame.Label', background=self.colors["panel"], foreground=self.colors["cyan"], font=('Segoe UI', 10, 'bold'))
        style.configure('TLabelframe', background=self.colors["panel"], bordercolor=self.colors["border"])
        
        # Labels
        style.configure('App.TLabel', background=self.colors["bg"], foreground=self.colors["text"], font=('Segoe UI', 10))
        style.configure('Panel.TLabel', background=self.colors["panel"], foreground=self.colors["text"], font=('Segoe UI', 10))
        style.configure('Title.TLabel', background=self.colors["bg"], foreground=self.colors["text"], font=('Segoe UI', 16, 'bold'))
        style.configure('PanelTitle.TLabel', background=self.colors["panel"], foreground=self.colors["text"], font=('Segoe UI', 16, 'bold'))
        style.configure('Help.TLabel', background=self.colors["panel"], foreground=self.colors["muted"], font=('Segoe UI', 8))
        style.configure('Success.TLabel', background=self.colors["panel"], foreground=self.colors["ok"], font=('Segoe UI', 8))
        style.configure('Error.TLabel', background=self.colors["panel"], foreground=self.colors["red"], font=('Segoe UI', 8))
        style.configure('Chip.TLabel', background=self.colors["panel_2"], foreground=self.colors["purple"], font=('Segoe UI', 9, 'bold'))
        
        # Entradas y Combobox (Se utiliza estilo básico porque Tkinter clásico a veces es mejor para dark mode)
        style.configure('TEntry', fieldbackground=self.colors["panel_2"], foreground=self.colors["text"], insertcolor=self.colors["text"], bordercolor=self.colors["border"])
        style.configure('TCombobox', fieldbackground=self.colors["panel_2"], foreground=self.colors["text"], selectbackground=self.colors["blue"])
        
        # Botones Principales
        style.configure('Primary.TButton', background=self.colors["blue"], foreground="white", font=('Segoe UI', 10, 'bold'), padding=6)
        style.map('Primary.TButton', background=[('active', self.colors["purple"]), ('disabled', self.colors["muted"])])
        
        # Botones Secundarios y Peligro
        style.configure('Secondary.TButton', background=self.colors["panel_2"], foreground=self.colors["text"], font=('Segoe UI', 10), padding=6)
        style.map('Secondary.TButton', background=[('active', self.colors["border"])])
        
        style.configure('Danger.TButton', background=self.colors["red"], foreground="white", font=('Segoe UI', 10, 'bold'), padding=6)
        style.map('Danger.TButton', background=[('active', "#b91c1c")])
        
        # Treeview (Tablas)
        style.configure('Treeview', background=self.colors["panel_2"], foreground=self.colors["text"], fieldbackground=self.colors["panel_2"], bordercolor=self.colors["border"], font=('Segoe UI', 10))
        style.configure('Treeview.Heading', background=self.colors["panel"], foreground=self.colors["muted"], font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', self.colors["blue"])])
        
        # Checkbuttons y Radiobuttons
        style.configure('TCheckbutton', background=self.colors["panel"], foreground=self.colors["text"])
        style.map('TCheckbutton', background=[('active', self.colors["panel"])])
        style.configure('TRadiobutton', background=self.colors["panel"], foreground=self.colors["text"])
        style.map('TRadiobutton', background=[('active', self.colors["panel"])])

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        # Si la vista tiene un método on_show, se ejecuta cada vez que se muestra la pantalla
        if hasattr(frame, "on_show") and callable(getattr(frame, "on_show")):
            frame.on_show()

class BaseFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style='App.TFrame')
        self.controller = controller
        
        # Toast Notifications
        self.toast_frame = tk.Frame(self, bg=self.controller.colors["bg"])
        self.toast_label = tk.Label(self.toast_frame, text="", font=("Segoe UI", 10, "bold"), pady=8, padx=10)
        self.toast_label.pack(fill="x")
        
    def show_toast(self, message, msg_type="info"):
        self.toast_frame.pack(side="bottom", fill="x", pady=10, padx=20)
        self.toast_label.config(text=message)
        colors = self.controller.colors
        if msg_type == "success":
            self.toast_label.config(bg=colors["ok"], fg="#000000")
        elif msg_type == "error":
            self.toast_label.config(bg=colors["red"], fg="#ffffff")
        elif msg_type == "warn":
            self.toast_label.config(bg=colors["warn"], fg="#000000")
        else:
            self.toast_label.config(bg=colors["blue"], fg="#ffffff")
        # Auto-ocultar después de 4 segundos
        self.after(4000, self.hide_toast)

    def hide_toast(self):
        self.toast_frame.pack_forget()

    def build_nav(self):
        nav_frame = ttk.Frame(self, style='Panel.TFrame')
        nav_frame.pack(side="top", fill="x", pady=(0, 10))
        
        ttk.Label(nav_frame, text="Mini-Git", font=("Segoe UI", 14, "bold"), foreground=self.controller.colors["purple"], background=self.controller.colors["panel"]).pack(side="left", padx=20, pady=10)
        
        views = [
            ("Repos", "HU009_ListarRepositorios"), ("Crear", "HU003_CrearRepo"),
            ("Commit", "HU004_Commit"), ("Historial", "HU005_Historial"),
            ("Diff", "HU006_Diff"), ("Ramas", "HU007_Ramas"),
            ("Merge", "HU008_Merge"), ("Eliminar", "HU010_EliminarRepo"),
            ("Salir", "HU001_Login")
        ]
        
        for text, frame_name in views:
            btn = ttk.Button(nav_frame, text=text, style='Secondary.TButton', command=lambda f=frame_name: self.controller.show_frame(f))
            btn.pack(side="left", padx=2)

def formatear_fecha_relativa(fecha_val):
    if not fecha_val:
        return "Sin registros"
    import datetime
    if isinstance(fecha_val, str):
        try:
            fecha_val = datetime.datetime.strptime(fecha_val, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(fecha_val)
    if isinstance(fecha_val, (datetime.datetime, datetime.date)):
        if isinstance(fecha_val, datetime.date) and not isinstance(fecha_val, datetime.datetime):
            fecha_val = datetime.datetime.combine(fecha_val, datetime.time.min)
        ahora = datetime.datetime.now()
        diff = ahora - fecha_val
        seg = diff.total_seconds()
        if seg < 60:
            return "Hace un momento"
        elif seg < 3600:
            return f"Hace {int(seg // 60)} min"
        elif seg < 86400:
            return f"Hace {int(seg // 3600)} h"
        elif seg < 2592000:
            return f"Hace {int(seg // 86400)} d"
        else:
            return fecha_val.strftime("%Y-%m-%d")
    return str(fecha_val)

class HU001_Login(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        box = ttk.Frame(self, style='Panel.TFrame', padding=40)
        box.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(box, text="Bienvenido a Mini-Git", style='PanelTitle.TLabel').pack(pady=(0, 20))
        
        ttk.Label(box, text="Usuario", style='Panel.TLabel').pack(anchor="w")
        self.user_input = tk.Entry(box, bg=self.controller.colors["panel_2"], fg="white", insertbackground="white", font=("Segoe UI", 11), relief="flat")
        self.user_input.pack(fill="x", pady=(0, 15), ipady=5)
        self.user_input.bind("<KeyRelease>", self.check_inputs)
        
        ttk.Label(box, text="Contraseña", style='Panel.TLabel').pack(anchor="w")
        self.pass_input = tk.Entry(box, show="*", bg=self.controller.colors["panel_2"], fg="white", insertbackground="white", font=("Segoe UI", 11), relief="flat")
        self.pass_input.pack(fill="x", pady=(0, 5), ipady=5)
        self.pass_input.bind("<KeyRelease>", self.check_inputs)
        
        # Recuperar contraseña (agregado)
        ttk.Button(box, text="¿Olvidaste tu contraseña?", style='Secondary.TButton', command=self.recover_pass).pack(anchor="e", pady=(0, 15))
        
        self.login_btn = ttk.Button(box, text="Ingresar", style='Primary.TButton', command=self.do_login, state="disabled")
        self.login_btn.pack(fill="x", pady=5)
        
        ttk.Button(box, text="Crear Cuenta", style='Secondary.TButton', command=lambda: controller.show_frame("HU002_Registro")).pack(fill="x", pady=5)
        
    def check_inputs(self, event=None):
        if self.user_input.get().strip() and self.pass_input.get().strip():
            self.login_btn.config(state="normal")
            self.show_toast("Datos completos. El botón ingresar ya está activo.", "info")
        else:
            self.login_btn.config(state="disabled")
            
    def do_login(self):
        correo = self.user_input.get().strip()
        password = self.pass_input.get().strip()
        
        self.login_btn.config(text="Verificando...", state="disabled")
        #self.show_toast("Validando credenciales contra el servicio de autenticación...", "info")
        #self.after(1000, self.hide_toast())
        
        try:
            # Llamada directa al método de autenticación del Facade
            usuario = self.controller.facade.autenticar(correo, password)
            if usuario:
                self.controller.set_usuario_actual(usuario)
                #self.show_toast("✓ Inicio de sesión exitoso.", "success")
                self.user_input.delete(0, "end")
                self.pass_input.delete(0, "end")
                self.login_btn.config(text="Ingresar")
                #self.after(1400, self.hide_toast())
                self.controller.show_frame("HU009_ListarRepositorios")
            else:
                #self.show_toast("✗ Credenciales inválidas.", "error")
                self.login_btn.config(text="Ingresar", state="normal")
                #self.after(1400, self.hide_toast())
        except Exception as e:
            #self.show_toast(f"Error al autenticar: {e}", "error")
            self.login_btn.config(text="Ingresar", state="normal")
            #self.after(1400, self.hide_toast())
            
    def recover_pass(self):
        pass
        #self.show_toast("✓ Enlace enviado. Revisa tu bandeja de entrada.", "success")
        #self.after(1500, self.hide_toast())

class HU002_Registro(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        box = ttk.Frame(self, style='Panel.TFrame', padding=30)
        box.place(relx=0.5, rely=0.5, anchor="center")
        
        ttk.Label(box, text="Crear Nueva Cuenta", style='PanelTitle.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        self.inputs = {}
        self.helps = {}
        fields = [
            ("Nombre Completo", "nameHelp"), 
            ("Email", "emailHelp"), 
            ("Usuario", "userHelp"), 
            ("Contraseña", "passHelp"), 
            ("Confirmar", "pass2Help")
        ]
        
        for i, (f, help_id) in enumerate(fields):
            ttk.Label(box, text=f, style='Panel.TLabel').grid(row=i*2+1, column=0, sticky="w", padx=5)
            ent = tk.Entry(box, show="*" if "Contraseña" in f or "Confirmar" in f else "", bg=self.controller.colors["panel_2"], fg="white", font=("Segoe UI", 10), relief="flat")
            ent.grid(row=i*2+1, column=1, pady=5, padx=5, sticky="ew", ipady=4)
            ent.bind("<KeyRelease>", self.validate_form)
            self.inputs[f] = ent
            
            help_lbl = ttk.Label(box, text="", style='Help.TLabel')
            help_lbl.grid(row=i*2+2, column=1, sticky="w", padx=5)
            self.helps[f] = help_lbl
            
        self.terms_var = tk.BooleanVar()
        ttk.Checkbutton(box, text="Acepto términos y condiciones", variable=self.terms_var, command=self.validate_form, style='TCheckbutton').grid(row=11, column=0, columnspan=2, pady=10)
        
        self.reg_btn = ttk.Button(box, text="Registrarse", style='Primary.TButton', command=self.register, state="disabled")
        self.reg_btn.grid(row=12, column=0, columnspan=2, sticky="ew", pady=5)
        
        ttk.Button(box, text="Cancelar", style='Secondary.TButton', command=lambda: controller.show_frame("HU001_Login")).grid(row=13, column=0, columnspan=2, sticky="ew")
        
    def validate_form(self, event=None):
        name = self.inputs["Nombre Completo"].get()
        email = self.inputs["Email"].get()
        user = self.inputs["Usuario"].get()
        p1 = self.inputs["Contraseña"].get()
        p2 = self.inputs["Confirmar"].get()
        
        name_ok = 5 <= len(name) <= 100
        self.helps["Nombre Completo"].config(text="✓ Nombre válido" if name_ok else "⚠️ 5 a 100 caracteres", style='Success.TLabel' if name_ok else 'Help.TLabel')
        
        email_ok = re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email)
        self.helps["Email"].config(text="✓ Email válido" if email_ok else "⚠️ Formato inválido", style='Success.TLabel' if email_ok else 'Help.TLabel')
        
        user_ok = re.match(r"^[a-zA-Z0-9_]{3,20}$", user)
        self.helps["Usuario"].config(text="✓ Username válido" if user_ok else "⚠️ 3-20 caracteres alfanuméricos", style='Success.TLabel' if user_ok else 'Help.TLabel')
        
        pass_ok = len(p1) >= 8 and any(c.isupper() for c in p1) and any(c.isdigit() for c in p1)
        self.helps["Contraseña"].config(text="✓ Segura" if pass_ok else "⚠️ Min 8 chars, 1 mayúscula, 1 número", style='Success.TLabel' if pass_ok else 'Help.TLabel')
        
        match_ok = (p1 == p2) and len(p1) > 0
        self.helps["Confirmar"].config(text="✓ Coinciden" if match_ok else "✗ No coinciden", style='Success.TLabel' if match_ok else 'Error.TLabel')
        
        if name_ok and email_ok and user_ok and pass_ok and match_ok and self.terms_var.get():
            self.reg_btn.config(state="normal")
        else:
            self.reg_btn.config(state="disabled")
            
    def register(self):
        nombre = self.inputs["Nombre Completo"].get().strip()
        email = self.inputs["Email"].get().strip()
        usuario = self.inputs["Usuario"].get().strip()
        password = self.inputs["Contraseña"].get().strip()

        # Invocación a Facade: registrar_usuario(nombre, correo, password)
        try:
            res = self.controller.facade.registrar(nombre, email, usuario, password)
            if res:
                #self.show_toast("✓ Cuenta creada con éxito en la base de datos.", "success")
                for ent in self.inputs.values(): ent.delete(0, 'end')
                for lbl in self.helps.values(): lbl.config(text="")
                self.terms_var.set(False)
                #self.after(1400, self.hide_toast())
                self.controller.show_frame("HU001_Login")
            else:
                pass
                #self.show_toast("✗ No se pudo registrar la cuenta.", "error")
                #self.after(1400, self.hide_toast())
        except Exception as e:
            pass
            #self.show_toast(f"Error al registrar usuario: {e}", "error")
            #self.after(1400, self.hide_toast())
        #self.show_toast("✓ Cuenta creada. Se envió correo de confirmación.", "success")
        for ent in self.inputs.values(): ent.delete(0, 'end')
        for lbl in self.helps.values(): lbl.config(text="")
        self.terms_var.set(False)
        #self.hide_toast()

class HU009_ListarRepositorios(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        self.repos = []
        self.filtered_repos = []
        self.search_var = tk.StringVar()
        self.filter_vis_var = tk.StringVar(value="Todos")

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.build_nav()

        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        # Top Bar
        top_bar = ttk.Frame(content, style='App.TFrame')
        top_bar.pack(fill="x", pady=(0, 10))
        ttk.Label(top_bar, text="Mis Repositorios", style='Title.TLabel').pack(side="left")
        ttk.Button(top_bar, text="+ Nuevo Repositorio", style='Primary.TButton', command=lambda: self.controller.show_frame("HU003_CrearRepo")).pack(side="right")

        user_id = (
            self.controller.usuario_actual["id"]
            if isinstance(self.controller.usuario_actual, dict)
            else (self.controller.usuario_actual.id if self.controller.usuario_actual else 1)
        )
        try:
            self.repos = self.controller.facade.listar_proyectos_usuario(user_id)
            total_commits = self.controller.facade.contar_commits_totales_usuario(user_id)
        except Exception as e:
            #self.show_toast(f"Error cargando repositorios: {e}", "error")
            self.repos = []
            total_commits = 0

        # Estadísticas basadas en objetos Proyecto
        total_repos = len(self.repos)
        privados = sum(1 for r in self.repos if r.visibilidad.lower() == "privado")
        publicos = total_repos - privados
        #self.hide_toast()

        stats_frame = ttk.Frame(content, style='App.TFrame')
        stats_frame.pack(fill="x", pady=(0, 20))

        stats = [
            ("Total Repos", str(total_repos), self.controller.colors["blue"]), 
                 ("Privados", str(privados), self.controller.colors["purple"]), 
                 ("Públicos", str(publicos), self.controller.colors["ok"]),
                 ("Commits Totales", str(total_commits), self.controller.colors["cyan"])
        ]

        for title, val, color in stats:
            card = ttk.Frame(stats_frame, style='Panel.TFrame')
            card.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
            ttk.Label(card, text=title, font=("Segoe UI", 9), foreground=self.controller.colors["muted"], background=self.controller.colors["panel"]).pack(anchor="center")
            ttk.Label(card, text=val, font=("Segoe UI", 16, "bold"), foreground=color, background=self.controller.colors["panel"]).pack(anchor="center")
        
        filters = ttk.Frame(content, style='App.TFrame')
        filters.pack(fill="x", pady=(0, 15))

        # Buscador por texto
        ttk.Label(
            filters,
            text="Buscar repositorios:",
            font=("Segoe UI", 9),
            style='App.TLabel'
            #foreground=self.controller.colors["fg"],
        ).pack(side="left", padx=(15, 5))
        self.search = ttk.Entry(filters, textvariable=self.search_var, font=("Segoe UI", 10))
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        #self.search.insert(0, "Buscar repositorios...")
        self.search.bind("<KeyRelease>", lambda e: self.apply_filters())
        self.search.delete(0, "end")
        
        ttk.Label(filters, text="Privacidad:", style='App.TLabel').pack(side="left", padx=5)
        self.privacy_filter = ttk.Combobox(filters, textvariable=self.filter_vis_var, values=["Todos", "Público", "Privado"], state="readonly", width=10)
        self.privacy_filter.current(0)
        self.privacy_filter.pack(side="left", padx=5)
        self.privacy_filter.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())
        
        ttk.Button(filters, text="Tarjetas", style='Secondary.TButton', command=self.show_cards).pack(side="left", padx=2)
        ttk.Button(filters, text="Tabla", style='Secondary.TButton', command=self.show_table).pack(side="left", padx=2)
        
        # Contenedores de Vistas
        self.cards_frame = ttk.Frame(content, style='App.TFrame')
        self.table_frame = ttk.Frame(content, style='App.TFrame')

        #self.build_cards()
        #self.build_table()
        self.apply_filters()
        self.show_cards()

    def apply_filters(self):
        """Filtra la lista de repositorios según el término de búsqueda y la visibilidad."""
        search_text = self.search_var.get().strip().lower()
        selected_vis = self.filter_vis_var.get().replace("ú","u")

        self.filtered_repos = []
        for repo in self.repos:
            nombre = str(repo.nombre).lower()
            descripcion = str(repo.descripcion).lower()
            visibilidad = str(repo.visibilidad)

            coincide_texto = (search_text in nombre) or (search_text in descripcion)
            coincide_vis = (selected_vis == "Todos") or (visibilidad.lower() == selected_vis.lower())

            if coincide_texto and coincide_vis:
                self.filtered_repos.append(repo)

        self.build_cards()
        self.build_table()

    def build_cards(self):
        for widget in self.cards_frame.winfo_children(): widget.destroy()

        if not self.filtered_repos:
            ttk.Label(
                self.cards_frame,
                text="No se encontraron repositorios que coincidan con los filtros.",
                font=("Segoe UI", 10, "italic"),
                foreground=self.controller.colors["muted"],
            ).pack(pady=30)
            return

        # Contenedor con Canvas y Scrollbars (Horizontal y Vertical)
        canvas = tk.Canvas(
            self.cards_frame,
            bg=self.controller.colors["bg"],
            highlightthickness=0,
            bd=0
        )
        v_scrollbar = ttk.Scrollbar(self.cards_frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.cards_frame, orient="horizontal", command=canvas.xview)

        scrollable_frame = ttk.Frame(canvas, style="App.TFrame")
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Iteración sobre las instancias de la clase Proyecto
        #for repo in self.repos:
        for repo in self.filtered_repos:
            r_id = repo.id
            name = repo.nombre
            priv = repo.visibilidad
            desc = repo.descripcion
            date = repo.fecha_creacion
            ruta = repo.ruta

            # Consultas a Facade
            lenguaje = self.controller.facade.obtener_lenguaje_proyecto(r_id, ruta)
            u_fecha = self.controller.facade.obtener_ultima_actualizacion(r_id, date)
            u_fecha_str = formatear_fecha_relativa(u_fecha)

            card = ttk.Frame(scrollable_frame, style='Panel.TFrame')
            card.pack(fill="x", pady=5, ipady=10, ipadx=10)
            
            # Info izquierda
            info_frame = ttk.Frame(card, style='Panel.TFrame')
            info_frame.pack(side="left", fill="y")
            ttk.Label(info_frame, text=name, font=("Segoe UI", 12, "bold"), foreground=self.controller.colors["blue"], background=self.controller.colors["panel"]).pack(side="left", padx=(0, 10))
            ttk.Label(info_frame, text=priv, style='Chip.TLabel').pack(side="left", padx=5)
            ttk.Label(info_frame, text=desc, style='Panel.TLabel').pack(side="left", padx=5)
            ttk.Label(info_frame, text=date, style='Help.TLabel').pack(side="left", padx=10)
            
            # Botones derecha
            action_frame = ttk.Frame(card, style='Panel.TFrame')
            action_frame.pack(side="right")
            ttk.Button(action_frame, text="+ Commit", style='Secondary.TButton', command=lambda r=repo: self.ir_a_crear_commit(r)).pack(side="left", padx=2)
            ttk.Button(action_frame, text="Commits", style='Secondary.TButton', command=lambda r=repo: self.ir_a_historial(r)).pack(side="left", padx=2)
            ttk.Button(action_frame, text="Diff", style='Secondary.TButton', command=lambda r=repo: self.ir_a_diff(r)).pack(side="left", padx=2)
            ttk.Button(action_frame, text="Ramas", style='Secondary.TButton', command=lambda r=repo: self.ir_a_ramas(r)).pack(side="left", padx=2)
            ttk.Button(action_frame, text="Eliminar", style='Danger.TButton', command=lambda r=repo: self.ir_a_eliminar_repo(r)).pack(side="left", padx=2)

            # Detalles del repositorio
            details = ttk.Frame(card, style="Panel.TFrame")
            details.pack(fill="x", pady=(8, 0))

            ttk.Label(
                details,
                text=f"• Lenguaje: {lenguaje}",
                font=("Segoe UI", 9),
                foreground=self.controller.colors["purple"],
                background=self.controller.colors["panel"],
            ).pack(side="left", padx=(0, 15))

            ttk.Label(
                details,
                text=f"Actualizado: {u_fecha_str}",
                font=("Segoe UI", 9),
                foreground=self.controller.colors["muted"],
                background=self.controller.colors["panel"],
            ).pack(side="left")

    def build_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        if not self.repos:
            ttk.Label(
                self.table_frame,
                text="No tienes repositorios creados aún. Haz clic en '+ Nuevo Repositorio' para comenzar.",
                font=("Segoe UI", 10, "italic"),
                foreground=self.controller.colors["muted"],
            ).pack(pady=30)
            return

        if not self.filtered_repos:
            ttk.Label(
                self.table_frame,
                text="No se encontraron repositorios que coincidan con los filtros.",
                font=("Segoe UI", 10, "italic"),
                foreground=self.controller.colors["muted"],
            ).pack(pady=30)
            return
            
        columns = ("nombre", "visibilidad", "lenguaje", "actualizado")
        tree = ttk.Treeview(self.table_frame, columns=columns, show="headings", height=8)
        
        tree.heading("nombre", text="Nombre")
        tree.heading("visibilidad", text="Visibilidad")
        tree.heading("lenguaje", text="Lenguaje")
        tree.heading("actualizado", text="Última Actualización")
        
        tree.column("nombre", width=200)
        tree.column("visibilidad", width=100)
        tree.column("lenguaje", width=120)
        tree.column("actualizado", width=180)
        
        #for repo in self.repos:
        for repo in self.filtered_repos:
            r_id = repo.id
            nombre = repo.nombre
            visibilidad = repo.visibilidad
            ruta = repo.ruta
            f_creacion = repo.fecha_creacion
            
            lenguaje = self.controller.facade.obtener_lenguaje_proyecto(r_id, ruta)
            u_fecha = self.controller.facade.obtener_ultima_actualizacion(r_id, f_creacion)
            u_fecha_str = formatear_fecha_relativa(u_fecha)
            
            tree.insert("", "end", values=(nombre, visibilidad, lenguaje, u_fecha_str))
            
        tree.pack(fill="both", expand=True)

    def show_cards(self):
        self.table_frame.pack_forget()
        self.cards_frame.pack(fill="both", expand=True)

    def show_table(self):
        self.cards_frame.pack_forget()
        self.table_frame.pack(fill="both", expand=True)

    def ir_a_crear_commit(self, repo):
        """Asigna el repositorio seleccionado al controlador y abre la vista de crear commit."""
        self.controller.set_proyecto_actual(repo)
        #self.show_toast(f"Proyecto seleccionado: {repo.nombre}", "info")
        self.controller.show_frame("HU004_Commit")

    def ir_a_historial(self, repo):
        """Asigna el repositorio seleccionado al controlador y abre la vista de historial."""
        self.controller.set_proyecto_actual(repo)
        self.controller.show_frame("HU005_Historial")

    def ir_a_diff(self, repo):
        """Asigna el repositorio seleccionado al controlador y abre la vista de historial."""
        self.controller.set_proyecto_actual(repo)
        self.controller.show_frame("HU006_Diff")

    def ir_a_ramas(self, repo):
        """Asigna el repositorio seleccionado al controlador y abre la vista de ramas."""
        self.controller.set_proyecto_actual(repo)
        self.controller.show_frame("HU007_Ramas")

    def ir_a_eliminar_repo(self, repo):
        """Confirma y elimina un repositorio de la base de datos y disco."""
        self.controller.set_proyecto_actual(repo)
        self.controller.show_frame("HU010_EliminarRepo")

    def show_cards(self):
        self.table_frame.pack_forget()
        self.cards_frame.pack(fill="both", expand=True)

    def show_table(self):
        self.cards_frame.pack_forget()
        self.table_frame.pack(fill="both", expand=True)

class HU003_CrearRepo(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        
        box = ttk.Frame(self, style='Panel.TFrame', padding=30)
        box.pack(pady=20, fill="x", padx=40)
        
        ttk.Label(box, text="Crear Nuevo Repositorio", style='PanelTitle.TLabel').pack(anchor="w", pady=(0, 20))
        
        ttk.Label(box, text="Nombre del repositorio *", style='Panel.TLabel').pack(anchor="w")
        self.name_input = ttk.Entry(box, font=("Segoe UI", 11))
        self.name_input.pack(fill="x", pady=(0, 5))
        self.name_input.bind("<KeyRelease>", self.validate)
        
        self.help_lbl = ttk.Label(box, text="", style='Help.TLabel')
        self.help_lbl.pack(anchor="w", pady=(0, 10))
        
        ttk.Label(box, text="Descripción (opcional)", style='Panel.TLabel').pack(anchor="w")
        self.desc_input = ttk.Entry(box, font=("Segoe UI", 11))
        self.desc_input.pack(fill="x", pady=(0, 15))

        # Campo para Ruta del Proyecto
        ttk.Label(box, text="Ruta del proyecto", style="Panel.TLabel").pack(
            anchor="w"
        )
        path_frame = ttk.Frame(box, style="Panel.TFrame")
        path_frame.pack(fill="x", pady=(0, 15))

        self.path_input = ttk.Entry(path_frame, font=("Segoe UI", 11), state="readonly")
        self.path_input.pack(side="left", fill="x", expand=True, padx=(0, 10))

        self.browse_btn = ttk.Button(
            path_frame,
            text="Examinar...",
            style="Secondary.TButton",
            command=self.browse_folder,
        )
        self.browse_btn.pack(side="right")
        
        # Opciones de Privacidad
        ttk.Label(box, text="Privacidad", font=("Segoe UI", 10, "bold"), background=self.controller.colors["panel"], foreground=self.controller.colors["text"]).pack(anchor="w")
        self.priv_var = tk.StringVar(value="Público")
        ttk.Radiobutton(box, text="Público (Cualquiera en internet puede ver este repositorio)", variable=self.priv_var, value="Público", style='TRadiobutton').pack(anchor="w", pady=2)
        ttk.Radiobutton(box, text="Privado (Tú eliges quién puede ver y hacer commits)", variable=self.priv_var, value="Privado", style='TRadiobutton').pack(anchor="w", pady=(2, 15))
        
        # Inicialización (Checkboxes)
        ttk.Label(box, text="Inicializar este repositorio con:", font=("Segoe UI", 10, "bold"), background=self.controller.colors["panel"], foreground=self.controller.colors["text"]).pack(anchor="w")
        self.c_readme = tk.BooleanVar(value=True)
        self.c_git = tk.BooleanVar(value=False)
        self.c_lic = tk.BooleanVar(value=False)
        ttk.Checkbutton(box, text="Agregar README file", variable=self.c_readme, style='TCheckbutton').pack(anchor="w")
        ttk.Checkbutton(box, text="Agregar .gitignore", variable=self.c_git, style='TCheckbutton').pack(anchor="w")
        ttk.Checkbutton(box, text="Elegir una licencia", variable=self.c_lic, style='TCheckbutton').pack(anchor="w", pady=(0, 15))
        
        # Plantilla
        ttk.Label(box, text="Plantilla (Opcional)", style='Panel.TLabel').pack(anchor="w")
        self.template = ttk.Combobox(box, values=["Ninguna", "Python", "Node.js", "React", "Java"], state="readonly")
        self.template.current(0)
        self.template.pack(fill="x", pady=(0, 20))
        
        self.btn = ttk.Button(box, text="Crear Repositorio", style='Primary.TButton', command=self.create_repo, state="disabled")
        self.btn.pack(fill="x")

    def browse_folder(self):
        self.folder_selected = filedialog.askdirectory(title="Seleccionar carpeta del proyecto")
        if self.folder_selected:
            self.path_input.config(state="normal")
            self.path_input.delete(0, "end")
            self.path_input.insert(0, self.folder_selected)
            self.path_input.config(state="readonly")
        
    def validate(self, event=None):
        name = self.name_input.get().strip()
        if re.match(r"^[a-zA-Z0-9-]{3,50}$", name):
            self.btn.config(state="normal")
            self.help_lbl.config(text="✓ Nombre disponible", style='Success.TLabel')
        else:
            self.btn.config(state="disabled")
            self.help_lbl.config(text="⚠️ Usa 3-50 caracteres con letras, números o guion", style='Help.TLabel')
            
    def create_repo(self):
        user_id = (
            self.controller.usuario_actual["id"]
            if isinstance(self.controller.usuario_actual, dict)
            else (self.controller.usuario_actual.id if self.controller.usuario_actual else 1)
        )
        nombre = self.name_input.get().strip()
        descripcion = self.desc_input.get().strip()

        try:
            nuevo = self.controller.facade.crear_proyecto(
                user_id, nombre, descripcion, self.folder_selected, self.priv_var.get()
            )
            if nuevo:
                #self.show_toast(
                #    f"✓ Repositorio '{nombre}' creado con éxito.", "success"
                #)
                #self.after(1400, self.hide_toast())
                self.after(1500, self.controller.show_frame("HU009_ListarRepositorios"))
                #self.controller.show_frame("HU009_ListarRepositorios")
        except Exception as e:
            pass
            #self.show_toast(f"Error al crear repositorio: {e}", "error")
            #self.after(1400, self.hide_toast())

class HU004_Commit(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        self.cambios_detectados = []
        self.check_vars = {}
        self.diff_texto_actual = ""

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        box = ttk.Frame(self, style='App.TFrame', padding=20)
        box.pack(fill="both", expand=True)

        repo = self.controller.proyecto_actual
        if not repo:
            ttk.Label(box, text="Selecciona un repositorio primero en el listado.", style="Title.TLabel").pack(pady=20)
            return

        r_id = repo.id
        r_nombre = repo.nombre
        r_ruta = repo.ruta
        r_path_full = os.path.join(r_ruta, r_nombre) if r_ruta else ""
        # Consultar la rama activa de la base de datos
        rama_activa = self.controller.facade.obtener_rama_activa(r_id)
        fecha_repo = repo.fecha_creacion

        # Header Title
        top = ttk.Frame(box, style='App.TFrame')
        top.pack(fill="x")
        ttk.Label(top, text="Cambios Pendientes (Staging)", style='Title.TLabel').pack(side="left")
        ttk.Button(top, text="Ocultar/Mostrar Diff", style='Secondary.TButton', command=self.toggle_diff).pack(side="right")
        ttk.Button(top, text="◀️ Volver al Panel", style='Primary.TButton', command=self.ir_al_panel).pack(side="right")
        
        # Etiquetas (Repositorio, Autor, Rama, Fecha) - Meta Tags Chip Bar
        meta_frame = ttk.Frame(box, style='App.TFrame')
        meta_frame.pack(fill="x", pady=10)
    
        # 1. Nombre del Repositorio (Primero)
        ttk.Label(
            meta_frame, text=f"📁 Repo: {r_nombre}", font=("Segoe UI", 9, "bold"),
            style='Chip.TLabel'
        ).pack(side="left", padx=(0, 12))

        # 2. Autor
        user_name = self.controller.usuario_actual.nombre
        ttk.Label(
            meta_frame, text=f"👤 Autor: {user_name}", font=("Segoe UI", 9, "bold"),
            style='Chip.TLabel'
        ).pack(side="left", padx=(0, 12))

        # 3. Rama
        ttk.Label(
            meta_frame, text=f"🌿 Rama: {rama_activa.nombre}", font=("Segoe UI", 9, "bold"),
            style='Chip.TLabel'
        ).pack(side="left", padx=(0, 12))

        # 4. Fecha
        ttk.Label(
            meta_frame, text=f"📅 Fecha: {fecha_repo}", font=("Segoe UI", 9, "bold"),
            style='Chip.TLabel'
        ).pack(side="left")
        
        # Main Workspace: Left Staging Panel, Right Diff Panel
        paned = ttk.PanedWindow(box, orient="horizontal")
        paned.pack(fill="both", expand=True)

        # Left Panel (Staging & Actions)
        left_panel = ttk.Frame(paned, style="Panel.TFrame", padding=10)
        paned.add(left_panel, weight=1)

        ttk.Label(left_panel, text="Archivos con Cambios", font=("Segoe UI", 10, "bold"), foreground=self.controller.colors["blue"], background=self.controller.colors["panel"]).pack(anchor="w", pady=(0, 8))

        # Buttons Bar for Adding External Files / Refreshing
        btn_action_box = ttk.Frame(left_panel, style="Panel.TFrame")
        btn_action_box.pack(fill="x", pady=(0, 10))

        ttk.Button(
            btn_action_box, text="➕ Agregar Archivos", style="Secondary.TButton",
            command=lambda: self.agregar_archivos_externos(r_path_full)
        ).pack(side="left", padx=2)

        ttk.Button(
            btn_action_box, text="🔄 Refrescar", style="Secondary.TButton",
            command=lambda: self.cargar_cambios(r_id, r_path_full)
        ).pack(side="left", padx=2)

        # Scrollable Frame for Checkboxes
        self.files_container = ttk.Frame(left_panel, style="Panel.TFrame")
        self.files_container.pack(fill="both", expand=True)

        # Right Panel (Diff Viewer & Commit Form)
        self.diff_visible = True
        right_panel = ttk.Frame(paned, style="App.TFrame", padding=(10, 0, 0, 0))
        paned.add(right_panel, weight=3)

        ttk.Label(right_panel, text="Diferencias Detectadas (Diff)", font=("Segoe UI", 10, "bold"), foreground=self.controller.colors["fg"], background=self.controller.colors["bg"]).pack(anchor="w", pady=(0, 5))

        # Diff Text Box with Horizontal and Vertical Scrollbars
        diff_box = ttk.Frame(right_panel, style="App.TFrame")
        diff_box.pack(fill="both", expand=True, pady=(0, 10))

        self.txt_diff = tk.Text(
            diff_box, bg="#0d1117", fg="#e2e8f0", font=("Consolas", 9),
            wrap="none", highlightthickness=1, highlightbackground="#1e293b", bd=0
        )
        v_sc = ttk.Scrollbar(diff_box, orient="vertical", command=self.txt_diff.yview)
        h_sc = ttk.Scrollbar(diff_box, orient="horizontal", command=self.txt_diff.xview)
        self.txt_diff.configure(yscrollcommand=v_sc.set, xscrollcommand=h_sc.set)

        v_sc.pack(side="right", fill="y")
        h_sc.pack(side="bottom", fill="x")
        self.txt_diff.pack(side="left", fill="both", expand=True)

        # Configurar etiquetas de colores para el diff
        self.txt_diff.tag_config("blue", foreground="#38bdf8", font=("Consolas", 9, "bold"))
        self.txt_diff.tag_config("red", foreground="#f87171")
        self.txt_diff.tag_config("green", foreground="#4ade80")
        self.txt_diff.tag_config("context", foreground="#cbd5e1")

        # Commit Message Form
        msg_frame = ttk.Frame(right_panel, style="App.TFrame")
        msg_frame.pack(fill="x")

        ttk.Label(msg_frame, text="Mensaje del Commit:", font=("Segoe UI", 9, "bold"), foreground=self.controller.colors["fg"], background=self.controller.colors["bg"]).pack(anchor="w", pady=(0, 3))
        self.ent_msg = ttk.Entry(msg_frame, font=("Segoe UI", 10))
        self.ent_msg.pack(fill="x", pady=(0, 8))

        ttk.Label(msg_frame, text="Descripción Detallada (Opcional)", foreground=self.controller.colors["fg"], background=self.controller.colors["bg"]).pack(anchor="w", pady=(10, 0))
        self.desc_msg = tk.Text(msg_frame, height=4, bg=self.controller.colors["panel_2"], fg="white", font=("Segoe UI", 10), bd=1, relief="solid")
        self.desc_msg.pack(fill="x", pady=5)

        ttk.Button(
            msg_frame, text="🚀 Realizar Commit", style="Primary.TButton",
            command=lambda: self.ejecutar_commit(r_id)
        ).pack(fill="x")

        # Cargar los cambios iniciales
        self.cargar_cambios(r_id, r_path_full)

    def cargar_cambios(self, id_proyecto, ruta_proyecto):
        for w in self.files_container.winfo_children(): w.destroy()
        self.txt_diff.config(state="normal")
        self.txt_diff.delete("1.0", tk.END)

        res = self.controller.facade.escanean_y_calcular_diferencias(id_proyecto, ruta_proyecto)
        self.cambios_detectados = res.get("cambios", [])
        diff_texto = res.get("diff_texto", "")
        self.diff_texto_actual = diff_texto

        self.check_vars = {}
        if not self.cambios_detectados:
            ttk.Label(self.files_container, text="Sin cambios pendientes.", font=("Segoe UI", 9, "italic"), foreground=self.controller.colors["muted"], background=self.controller.colors["panel"]).pack(anchor="w", pady=10)
        else:
            for item in self.cambios_detectados:
                var = tk.BooleanVar(value=True)
                self.check_vars[item['nombre']] = (var, item)
                tag_tipo = " [Nuevo]" if item['es_nuevo'] else " [Modificado]"
                chk = tk.Checkbutton(
                    self.files_container, text=f"{item['nombre']}{tag_tipo}", variable=var,
                    bg=self.controller.colors["panel"], fg=self.controller.colors["fg"],
                    selectcolor=self.controller.colors["bg"], activebackground=self.controller.colors["panel"],
                    activeforeground=self.controller.colors["blue"], font=("Segoe UI", 9)
                )
                chk.pack(anchor="w", pady=2)

        # Insertar diff formateado línea por línea
        for line in diff_texto.splitlines(keepends=True):
            if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                self.txt_diff.insert(tk.END, line, "blue")
            elif line.startswith("-"):
                self.txt_diff.insert(tk.END, line, "red")
            elif line.startswith("+"):
                self.txt_diff.insert(tk.END, line, "green")
            else:
                self.txt_diff.insert(tk.END, line, "context")

        self.txt_diff.config(state="disabled")

    def agregar_archivos_externos(self, ruta_proyecto):
        if not ruta_proyecto or not os.path.exists(ruta_proyecto):
            #self.show_toast("No existe la carpeta del proyecto en disco.", "error")
            #self.after(1000, self.hide_toast())
            return

        archivos_sel = filedialog.askopenfilenames(title="Seleccionar archivos para el proyecto")
        if archivos_sel:
            for ruta_origen in archivos_sel:
                try:
                    nombre = os.path.basename(ruta_origen)
                    dest = os.path.join(ruta_proyecto, nombre)
                    shutil.copy(ruta_origen, dest)
                except Exception as e:
                    print(f"Error copiando archivo: {e}")

            repo = self.controller.proyecto_actual
            self.cargar_cambios(repo.id, ruta_proyecto)
            #self.show_toast("Archivos agregados al directorio del proyecto.", "info")
            ##self.after(1400, self.hide_toast())

    def ejecutar_commit(self, id_proyecto):
        mensaje = self.ent_msg.get().strip()
        descripcionOp = self.desc_msg.get("1.0", "end-1c").strip()
        if not mensaje:
            #self.show_toast("Escribe un mensaje descriptivo para el commit.", "error")
            #self.after(1400, self.hide_toast())
            return

        archivos_a_commitear = [
            item for nombre, (var, item) in self.check_vars.items() if var.get()
        ]

        if not archivos_a_commitear:
            #self.show_toast("Selecciona al menos un archivo para incluir en el commit.", "error")
            #self.after(1400, self.hide_toast())
            return

        user_id = self.controller.usuario_actual.id
        try:
            exito = self.controller.facade.crear_commit_completo(id_proyecto, user_id, archivos_a_commitear, mensaje, descripcionOp, self.diff_texto_actual)
            if exito:
                #self.show_toast("¡Commit realizado con éxito!", "info")
                #self.after(1000, self.hide_toast())
                self.controller.show_frame("HU009_ListarRepositorios")
            else:
                pass
                #self.show_toast("No se pudo completar el commit.", "error")
                #self.after(1400, self.hide_toast())
        except Exception as e:
            pass
            #self.show_toast(f"Error al hacer commit: {e}", "error")
            #self.after(1400, self.hide_toast())

    def toggle_diff(self):
            if self.diff_visible:
                self.diff_box.pack_forget()
            else:
                # Se reinserta antes del mensaje corto
                self.diff_box.pack(fill="x", pady=(5, 15), before=self.msg.master.winfo_children()[3]) 
            self.diff_visible = not self.diff_visible

    def ir_al_panel(self):
        self.controller.show_frame("HU009_ListarRepositorios")
        
    def save_commit(self):
        #self.show_toast("✓ Commit guardado exitosamente. Hash: a1b2c3d4e5f6", "success")
        #self.after(1400, self.hide_toast())
        self.msg.delete(0, 'end')
        self.desc.delete("1.0", "end")
        self.btn_save.config(state="disabled")
        
    def discard(self):
        #self.show_toast("Cambios descartados. Ya no hay archivos pendientes.", "error")
        #self.after(1400, self.hide_toast())
        self.msg.delete(0, 'end')
        self.desc.delete("1.0", "end")

class HU005_Historial(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.commits = []
        self.filtered_commits = []
        self.search_var = tk.StringVar()
        self.branch_var = tk.StringVar(value="Todas")
        self.autor_var = tk.StringVar()

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.search_var.set("")
        self.build_nav()

        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        repo = self.controller.proyecto_actual
        if not repo:
            ttk.Label(content, text="Selecciona un repositorio en el listado para consultar su historial.", style="Title.TLabel").pack(pady=30)
            return

        r_id = repo.id
        r_nombre = repo.nombre

        try:
            self.commits = self.controller.facade.obtener_historial_proyecto(r_id) or []
            rama_activa = self.controller.facade.obtener_rama_activa(r_id)
        except Exception as e:
            self.commits = []
            rama_activa = "main"

        top_bar = ttk.Frame(content, style="App.TFrame")
        top_bar.pack(fill="x", pady=(0, 10))
        ttk.Label(top_bar, text=f"Historial de Commits - {r_nombre}", style="Title.TLabel").pack(side="left")

        ttk.Button(
            top_bar, 
            text="◀️ Volver al Panel", 
            style='Primary.TButton', 
            command=lambda: self.controller.show_frame("HU009_ListarRepositorios")
        ).pack(side="right")
        
        # Tarjetas Estadísticas Superiores
        stats_frame = ttk.Frame(content, style='App.TFrame')
        stats_frame.pack(fill="x", pady=(0, 15))

        autores_unicos_n = len(set(c['autor'] for c in self.commits if 'autor' in c and c['autor']))
        #autores_unicos = list(c['autor'] for c in self.commits if 'autor' in c and c['autor'] and c not in autores_unicos)
        ult_fecha = self.commits[0]['fecha'] if self.commits else None
        
        stats = [("Total Commits", "345", self.controller.colors["blue"]), 
                 ("Autores", "4", self.controller.colors["purple"]), 
                 ("Días Activos", "120", self.controller.colors["ok"]), 
                 ("Líneas Modificadas", "+4.5k / -1.2k", self.controller.colors["warn"])]

        stats = [
            ("Total Commits", str(len(self.commits)), self.controller.colors["blue"]),
            ("Autores", str(autores_unicos_n), self.controller.colors["ok"]),
            ("Rama Activa", str(rama_activa.nombre), self.controller.colors["purple"]),
            ("Último Commit", formatear_fecha_relativa(ult_fecha), self.controller.colors["muted"]),
        ]
        for title, val, color in stats:
            card = ttk.Frame(stats_frame, style="Panel.TFrame")
            card.pack(side="left", fill="x", expand=True, padx=4, ipady=6)
            ttk.Label(card, text=title, font=("Segoe UI", 8), foreground=self.controller.colors["muted"], background=self.controller.colors["panel"]).pack(anchor="center")
            ttk.Label(card, text=val, font=("Segoe UI", 12, "bold"), foreground=color, background=self.controller.colors["panel"]).pack(anchor="center")
        
        filter_bar = ttk.Frame(content, style='App.TFrame')
        filter_bar.pack(fill="x", pady=5)

        autores_disponibles = ["Todos"]
        # Extracción dinámica de autores para el combobox
        for c in self.commits:
            r = c.get('autor') if isinstance(c, dict) else getattr(c, 'autor', None)
            if r and r not in autores_disponibles:
                autores_disponibles.append(r)
        
        ttk.Label(filter_bar, text="Autor:", style='App.TLabel').pack(side="left")
        self.author_combo = ttk.Combobox(filter_bar, textvariable=self.autor_var, values=autores_disponibles, state="readonly", width=15)
        self.author_combo.current(0)
        self.author_combo.pack(side="left", padx=5)
        self.author_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(
            filter_bar, 
            text="Filtrar por rama:", 
            font=("Segoe UI", 9), 
            style='App.TLabel'
        ).pack(side="left", padx=(0, 5))

        # Extracción dinámica de ramas para el combobox
        ramas_disponibles = ["Todas", rama_activa.nombre]
        for c in self.commits:
            r = c.get('rama') if isinstance(c, dict) else getattr(c, 'rama', None)
            if r and r not in ramas_disponibles:
                ramas_disponibles.append(r)

        self.branch_combo = ttk.Combobox(
            filter_bar, 
            textvariable=self.branch_var, 
            values=ramas_disponibles, 
            state="readonly", 
            width=15, 
            font=("Segoe UI", 9)
        )
        self.branch_combo.pack(side="left", padx=(0, 10))
        self.branch_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_filters())

        ttk.Label(
            filter_bar, 
            text="Buscar por mensaje, hash o autor:", 
            font=("Segoe UI", 9), 
            style='App.TLabel'
        ).pack(side="left", padx=(0, 5))

        self.search = ttk.Entry(filter_bar, textvariable=self.search_var, font=("Segoe UI", 10))
        self.search.pack(side="left", fill="x", expand=True, padx=5)
        self.search.bind("<KeyRelease>", lambda e: self.apply_filters())
        
        paned = ttk.PanedWindow(content, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=10)
        
        # Lista
        cols = ("hash", "mensaje", "autor", "rama", "fecha", "acciones")
        self.tree = ttk.Treeview(paned, columns=cols, show="headings", selectmode="browse")
        
        self.tree.heading("hash", text="Hash SHA-1")
        self.tree.heading("mensaje", text="Mensaje de Commit")
        self.tree.heading("autor", text="Autor")
        self.tree.heading("rama", text="Rama")
        self.tree.heading("fecha", text="Fecha y Hora")
        self.tree.heading("acciones", text="Acciones")

        self.tree.column("hash", width=100, minwidth=80)
        self.tree.column("mensaje", width=320, minwidth=180)
        self.tree.column("autor", width=120, minwidth=90)
        self.tree.column("rama", width=90, minwidth=70)
        self.tree.column("fecha", width=140, minwidth=110)
        self.tree.column("acciones", width=100, minwidth=80, anchor="center")
        #paned.add(self.tree, weight=2)

        v_sc = ttk.Scrollbar(paned, orient="vertical", command=self.tree.yview)
        h_sc = ttk.Scrollbar(paned, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_sc.set, xscrollcommand=h_sc.set)

        v_sc.pack(side="right", fill="y")
        h_sc.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select_commit)
        paned.add(self.tree, weight=2)
        
        # PANEL DERECHO: Detalles del commit e inspección de diferencias (Diff)
        right_frame = ttk.LabelFrame(paned, text="Detalles del Commit Seleccionado", style='TLabelframe', padding=12)
        paned.add(right_frame, weight=2)

        # Tarjeta de Metadata Superior
        self.meta_card = ttk.Frame(right_frame, style='Panel2.TFrame', padding=10)
        self.meta_card.pack(fill="x", pady=(0, 10))

        self.lbl_hash = ttk.Label(self.meta_card, text="SHA-1: -", font=("Segoe UI", 10, "bold"), foreground=self.controller.colors["cyan"], background=self.controller.colors["panel_2"])
        self.lbl_hash.pack(anchor="w")

        self.lbl_autor_rama = ttk.Label(self.meta_card, text="Autor: - | Rama: -", font=("Segoe UI", 9), foreground=self.controller.colors["text"], background=self.controller.colors["panel_2"])
        self.lbl_autor_rama.pack(anchor="w", pady=2)

        self.lbl_fecha = ttk.Label(self.meta_card, text="Fecha: -", font=("Segoe UI", 8), foreground=self.controller.colors["muted"], background=self.controller.colors["panel_2"])
        self.lbl_fecha.pack(anchor="w")

        ttk.Label(right_frame, text="Mensaje Completo:", font=("Segoe UI", 9, "bold"), style='Panel.TLabel').pack(anchor="w", pady=(5, 2))
        self.txt_msg = tk.Text(right_frame, height=3, bg=self.controller.colors["panel_2"], fg="white", font=("Segoe UI", 9), relief="flat", wrap="word")
        self.txt_msg.pack(fill="x", pady=(0, 10))

        ttk.Label(right_frame, text="Cambios / Diferencias (Diff):", font=("Segoe UI", 9, "bold"), style='Panel.TLabel').pack(anchor="w", pady=(5, 2))

        diff_box = ttk.Frame(right_frame, style='Panel.TFrame')
        diff_box.pack(fill="both", expand=True)

        self.txt_diff = tk.Text(
            diff_box, bg="#0d1117", fg="#e2e8f0", font=("Consolas", 9),
            wrap="none", highlightthickness=1, highlightbackground=self.controller.colors["border"], bd=0
        )
        v_sc_diff = ttk.Scrollbar(diff_box, orient="vertical", command=self.txt_diff.yview)
        h_sc_diff = ttk.Scrollbar(diff_box, orient="horizontal", command=self.txt_diff.xview)
        self.txt_diff.configure(yscrollcommand=v_sc_diff.set, xscrollcommand=h_sc_diff.set)

        v_sc_diff.pack(side="right", fill="y")
        h_sc_diff.pack(side="bottom", fill="x")
        self.txt_diff.pack(side="left", fill="both", expand=True)

        self.txt_diff.tag_config("header", foreground="#38bdf8", font=("Consolas", 9, "bold"))
        self.txt_diff.tag_config("add", foreground="#4ade80")
        self.txt_diff.tag_config("sub", foreground="#f87171")

        self.apply_filters()

    def apply_filters(self):
        st = self.search_var.get().strip().lower()
        selected_branch = self.branch_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.commits:
            return

        self.filtered_commits = []
        for c in self.commits:
            if isinstance(c, dict):
                msg = str(c.get('mensaje', ''))
                autor = str(c.get('autor', ''))
                hash_v = str(c.get('hash_version', ''))
                rama = str(c.get('rama', 'main'))
            else:
                msg = str(getattr(c, 'mensaje', ''))
                autor = str(getattr(c, 'autor', ''))
                hash_v = str(getattr(c, 'hash_version', ''))
                rama = str(getattr(c, 'rama', 'main'))

            match_text = (st in msg.lower()) or (st in autor.lower()) or (st in hash_v.lower())
            match_branch = (selected_branch == "Todas") or (rama.lower() == selected_branch.lower())

            if match_text and match_branch:
                self.filtered_commits.append(c)

        for c in self.filtered_commits:
            if isinstance(c, dict):
                hash_full = str(c.get('hash_version', ''))
                msg = str(c.get('mensaje', 'Sin mensaje'))
                autor = str(c.get('autor', 'Desconocido'))
                rama = str(c.get('rama', 'main'))
                fecha = c.get('fecha')
            else:
                hash_full = str(getattr(c, 'hash_version', ''))
                msg = str(getattr(c, 'mensaje', 'Sin mensaje'))
                autor = str(getattr(c, 'autor', 'Desconocido'))
                rama = str(getattr(c, 'rama', 'main'))
                fecha = getattr(c, 'fecha', None)

            hash_short = hash_full[:8] + "..." if len(hash_full) > 8 else hash_full
            f_str = formatear_fecha_relativa(fecha)

            self.tree.insert("", "end", values=(
                hash_short,
                msg,
                autor,
                rama,
                f_str,
                "Ver Detalle"
            ))

    def on_select_commit(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        index = self.tree.index(selected[0])
        if index < len(self.filtered_commits):
            commit = self.filtered_commits[index]
            
            hash_f = commit.get('hash_version', '-') if isinstance(commit, dict) else getattr(commit, 'hash_version', '-')
            autor = commit.get('autor', '-') if isinstance(commit, dict) else getattr(commit, 'autor', '-')
            rama = commit.get('rama', 'main') if isinstance(commit, dict) else getattr(commit, 'rama', 'main')
            fecha = commit.get('fecha', None) if isinstance(commit, dict) else getattr(commit, 'fecha', None)
            msg = commit.get('mensaje', '') if isinstance(commit, dict) else getattr(commit, 'mensaje', '')
            archivo = commit.get('nombre_archivo', 'archivo.py') if isinstance(commit, dict) else getattr(commit, 'nombre_archivo', 'archivo.py')
            zip_path = commit.get('contenido_comprimido', '') if isinstance(commit, dict) else getattr(commit, 'contenido_comprimido', '')

            # Actualizar panel de detalles a la derecha
            self.lbl_hash.config(text=f"SHA-1: {hash_f}")
            self.lbl_autor_rama.config(text=f"👤 Autor: {autor} | 🌿 Rama: {rama}")
            self.lbl_fecha.config(text=f"📅 Fecha: {formatear_fecha_relativa(fecha)}")

            self.txt_msg.config(state="normal")
            self.txt_msg.delete("1.0", tk.END)
            self.txt_msg.insert(tk.END, msg)
            self.txt_msg.config(state="disabled")

            # LECTURA DEL DIFF DIRECTAMENTE DESDE DIFF/DIFF.TXT DENTRO DEL ZIP DEL COMMIT
            # Renderizar el Diff con sintaxis de líneas añadidas y eliminadas (Estilo ventana crear commit)
            self.txt_diff.config(state="normal")
            self.txt_diff.delete("1.0", tk.END)

            lineas_diff = []
            id_proyecto = getattr(self.controller.proyecto_actual, 'id', None) if self.controller.proyecto_actual else None

            # LECTURA DE LA SUB-CARPETA VIRTUAL 'diff/diff.txt' DENTRO DEL UNICO ZIP
            # Resolver la ruta dinámicamente usando el nuevo método
            zip_valido = self.controller.facade.resolver_ruta_zip_valida(id_proyecto, zip_path, hash_f)
            #zip_valido = os.path.normpath(zip_path)
            #if zip_path and os.path.exists(zip_path):
            if zip_valido and os.path.exists(zip_path):
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zf:
                        print(zf.namelist())
                        # 1. Verificar si existe la entrada diff/diff.txt en el ZIP
                        if "diff/diff.txt" in zf.namelist():
                            contenido_diff = zf.read("diff/diff.txt").decode('utf-8', errors='replace')
                            lineas_diff = [line + '\n' for line in contenido_diff.splitlines()]
                        else:
                            # Fallback para commits antiguos sin diff/diff.txt
                            archivos_zip = [f for f in zf.namelist() if not f.startswith("diff/")]
                            if archivos_zip:
                                contenido = zf.read(archivos_zip[0]).decode('utf-8', errors='replace')
                                lineas_diff = [
                                    f"--- a/{archivo}\n",
                                    f"+++ b/{archivo}\n",
                                    f"@@ -0,0 +1,{len(contenido.splitlines())} @@\n"
                                ] + [f"+{linea}\n" for linea in contenido.splitlines()]
                except Exception as e:
                    lineas_diff = []

            if not lineas_diff:
                lineas_diff = [
                    f"--- a/{archivo}\n",
                    f"+++ b/{archivo}\n",
                    "@@ -1,4 +1,6 @@\n",
                    " import os\n",
                    f"+ # Commit registrado en rama [{rama}]\n",
                    f"+ # Mensaje: {msg}\n",
                    " def main():\n",
                    "-    # Código eliminado de la versión anterior\n",
                    "+    # Código actualizado y registrado en este commit\n",
                    "    return True\n"
                ]

            for line in lineas_diff:
                if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                    self.txt_diff.insert(tk.END, line, "header")
                elif line.startswith("-"):
                    self.txt_diff.insert(tk.END, line, "sub")
                elif line.startswith("+"):
                    self.txt_diff.insert(tk.END, line, "add")
                else:
                    self.txt_diff.insert(tk.END, line, "context")

            self.txt_diff.config(state="disabled")

class HU006_Diff(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.commits_map = {}
        self.diff_data = None
        self.vista_actual = "unificado" # 'unificado', 'lado_a_lado', 'estadisticas'

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.build_nav()
        
        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        ttk.Label(content, text="Repositorio: mi-proyecto-python", font=("Segoe UI", 10, "bold"), foreground=self.controller.colors["muted"], background=self.controller.colors["bg"]).pack(anchor="w")
        
        top = ttk.Frame(content, style='App.TFrame')
        top.pack(fill="x", pady=(5, 10))
        ttk.Label(top, text="Comparar Versiones (Diff)", style='Title.TLabel').pack(side="left")
        ttk.Button(top, text="◀️ Volver al Panel", style='Primary.TButton', command=lambda: self.controller.show_frame("HU009_ListarRepositorios")).pack(side="right")

        repo = self.controller.proyecto_actual
        if not repo:
            ttk.Label(content, text="Selecciona un repositorio en el panel primero para usar la herramienta Diff.", font=("Segoe UI", 11, "bold"), foreground=self.controller.colors["warn"], background=self.controller.colors["bg"]).pack(pady=40)
            return

        r_id = repo.id
        r_nombre = repo.nombre

        # Cargar historial de commits para llenar los comboboxes
        commits = self.controller.facade.obtener_historial_proyecto(r_id) or []

        ttk.Label(content, text=f"📁 Repositorio: {r_nombre}", font=("Segoe UI", 10, "bold"), foreground=self.controller.colors["cyan"], background=self.controller.colors["panel"]).pack(side="top", anchor=("w"), padx=(0, 15))
            
        # Selectores de Commits / Ramas
        select_frame = ttk.Frame(content, style='App.TFrame')
        select_frame.pack(fill="x", pady=5)

        self.commits_map = {}
        opciones_combo = []
        for c in commits:
            h_short = c['hash_version'][:8] if 'hash_version' in c else 'v'
            label = f"{h_short} - {c.get('mensaje', 'Sin mensaje')} ({formatear_fecha_relativa(c.get('fecha'))})"
            opciones_combo.append(label)
            self.commits_map[label] = c['id']

        ttk.Label(select_frame, text="Base:", style='App.TLabel').pack(side="left", padx=(10, 5))
        self.c_base = ttk.Combobox(select_frame, values=opciones_combo, state="readonly", width=78)
        self.c_base.pack(side="left", padx=5)
        
        ttk.Label(select_frame, text="vs  Comparar con:", style='App.TLabel').pack(side="left", padx=10)
        self.c_comp = ttk.Combobox(select_frame, values=opciones_combo, state="readonly", width=78)
        self.c_comp.pack(side="left", padx=5)

        if len(opciones_combo) >= 2:
            self.c_base.current(1)
            self.c_comp.current(0)
        elif len(opciones_combo) == 1:
            self.c_base.current(0)

        
        ttk.Button(select_frame, text="🔍 Comparar", style='Primary.TButton', command=self.do_compare).pack(side="left", padx=15)

        # Barra de Control de Vistas y Filtros
        tabs = ttk.Frame(content, style='App.TFrame')
        tabs.pack(fill="x", pady=10)
        ttk.Button(tabs, text="📄 Unificado", style='Secondary.TButton', command=lambda: self.cambiar_vista("unificado")).pack(side="left", padx=2)
        ttk.Button(tabs, text="📖 Lado a Lado", style='Secondary.TButton', command=lambda: self.cambiar_vista("lado_a_lado")).pack(side="left", padx=2)
        ttk.Button(tabs, text="📊 Estadísticas", style='Secondary.TButton', command=lambda: self.cambiar_vista("estadisticas")).pack(side="left", padx=2)

        self.lbl_resumen_cambios = ttk.Label(tabs, text="", font=("Segoe UI", 9, "bold"), foreground=self.controller.colors["muted"], background=self.controller.colors["bg"])
        self.lbl_resumen_cambios.pack(side="right", padx=10)
        
        actions = ttk.Frame(tabs, style='App.TFrame')
        actions.pack(side="right")
        ttk.Button(actions, text="Copiar Diff", style='Secondary.TButton', command=lambda: self.show_toast("✓ Copiado al portapapeles", "success")).pack(side="left", padx=2)

        # Contenedor dinámico principal
        self.diff_text = tk.Text(content, bg=self.controller.colors["panel"], fg=self.controller.colors["text"], font=("Consolas", 11))
        self.diff_text.pack(fill="both", expand=True)

        if len(opciones_combo) >= 2:
            self.do_compare()
        else:
            ttk.Label(self.diff_text, text="Se requieren al menos 2 commits realizados en el proyecto para realizar una comparación.", font=("Segoe UI", 10, "italic"), foreground=self.controller.colors["muted"]).pack(pady=40)

    def do_compare(self):
        val_a = self.c_base.get()
        val_b = self.c_comp.get()

        if not val_a or not val_b:
            print("Selecciona dos versiones para comparar.")
            #self.show_toast("Selecciona dos versiones para comparar.", "warn")
            return

        id_a = self.commits_map.get(val_a)
        id_b = self.commits_map.get(val_b)

        if not id_a or not id_b:
            print("Versiones no válidas.")
            #self.show_toast("Versiones no válidas.", "error")
            return

        try:
            self.diff_data = self.controller.facade.comparar_versiones(id_a, id_b)
            stats = self.diff_data['stats']
            #print(f"{self.diff_data}")
            self.lbl_resumen_cambios.config(
                text=f"📁 {stats['archivos_modificados']} archivo(s) cambiados |  +{stats['adiciones']} adiciones  |  -{stats['eliminaciones']} eliminaciones"
            )
            self.renderizar_vista()
        except Exception as e:
            print(f"Error al comparar versiones: {e}")
            #self.show_toast(f"Error al comparar versiones: {e}", "error")

    def cambiar_vista(self, modo):
        self.vista_actual = modo
        if self.diff_data:
            self.renderizar_vista()

    def renderizar_vista(self):
        for w in self.diff_text.winfo_children():
            w.destroy()

        if not self.diff_data:
            return

        if self.vista_actual == "unificado":
            self._render_unificado()
        elif self.vista_actual == "lado_a_lado":
            self._render_lado_a_lado()
        elif self.vista_actual == "estadisticas":
            self._render_estadisticas()

    def _render_unificado(self):
        diff_text_str = self.diff_data.get('raw_unified_diff', '')

        txt_box = tk.Text(
            self.diff_text, bg="#0d1117", fg="#e2e8f0",
            font=("Consolas", 10), wrap="none", highlightthickness=1,
            highlightbackground=self.controller.colors["border"], bd=0
        )
        v_sc = ttk.Scrollbar(self.diff_text, orient="vertical", command=txt_box.yview)
        h_sc = ttk.Scrollbar(self.diff_text, orient="horizontal", command=txt_box.xview)
        txt_box.configure(yscrollcommand=v_sc.set, xscrollcommand=h_sc.set)

        v_sc.pack(side="right", fill="y")
        h_sc.pack(side="bottom", fill="x")
        txt_box.pack(side="left", fill="both", expand=True)

        txt_box.tag_config("header", foreground="#38bdf8", font=("Consolas", 10, "bold"))
        txt_box.tag_config("add", foreground="#4ade80", background="#064e3b")
        txt_box.tag_config("sub", foreground="#f87171", background="#7f1d1d")
        txt_box.tag_config("context", foreground="#cbd5e1")

        if not diff_text_str.strip():
            txt_box.insert(tk.END, "Las versiones seleccionadas son idénticas. No se detectaron diferencias.")
        else:
            for line in diff_text_str.splitlines(keepends=True):
                if line.startswith("---") or line.startswith("+++") or line.startswith("@@"):
                    txt_box.insert(tk.END, line, "header")
                elif line.startswith("-"):
                    txt_box.insert(tk.END, line, "sub")
                elif line.startswith("+"):
                    txt_box.insert(tk.END, line, "add")
                else:
                    txt_box.insert(tk.END, line, "context")

        txt_box.config(state="disabled")

    def _render_lado_a_lado(self):
        archivos = self.diff_data.get('archivos_detalle', [])

        if not archivos:
            ttk.Label(self.diff_text, text="No hay diferencias entre las versiones seleccionadas.", font=("Segoe UI", 10, "italic"), foreground=self.controller.colors["muted"]).pack(pady=30)
            return

        notebook = ttk.Notebook(self.diff_text)
        notebook.pack(fill="both", expand=True)

        for arch in archivos:
            tab = ttk.Frame(notebook, style='App.TFrame')
            notebook.add(tab, text=f"📄 {arch['nombre']} (+{arch['adiciones']} / -{arch['eliminaciones']})")

            paned = ttk.PanedWindow(tab, orient="horizontal")
            paned.pack(fill="both", expand=True, pady=5)

            # Panel Izquierdo: Versión Base (A)
            left_frame = ttk.LabelFrame(paned, text="Versión Base (A)", style='TLabelframe')
            txt_a = tk.Text(left_frame, bg="#0d1117", fg="#cbd5e1", font=("Consolas", 9), wrap="none", bd=0)
            v_sc_a = ttk.Scrollbar(left_frame, orient="vertical", command=txt_a.yview)
            txt_a.configure(yscrollcommand=v_sc_a.set)
            v_sc_a.pack(side="right", fill="y")
            txt_a.pack(fill="both", expand=True)
            paned.add(left_frame, weight=1)

            # Panel Derecho: Versión Comparar (B)
            right_frame = ttk.LabelFrame(paned, text="Versión Comparar (B)", style='TLabelframe')
            txt_b = tk.Text(right_frame, bg="#0d1117", fg="#cbd5e1", font=("Consolas", 9), wrap="none", bd=0)
            v_sc_b = ttk.Scrollbar(right_frame, orient="vertical", command=txt_b.yview)
            txt_b.configure(yscrollcommand=v_sc_b.set)
            v_sc_b.pack(side="right", fill="y")
            txt_b.pack(fill="both", expand=True)
            paned.add(right_frame, weight=1)

            # Configurar etiquetas de resaltado sintáctico
            for txt in (txt_a, txt_b):
                txt.tag_config("deleted", foreground="#f87171", background="#451a1a")
                txt.tag_config("added", foreground="#4ade80", background="#143823")
                txt.tag_config("modified", foreground="#fde047", background="#3f3c1d")
                txt.tag_config("normal", foreground="#e2e8f0")
                txt.tag_config("empty", background="#070b17")

            for num_a, val_a, type_a, num_b, val_b, type_b in arch['side_by_side']:
                line_a_fmt = f"{num_a:>4} | {val_a}\n" if val_a or num_a else "\n"
                line_b_fmt = f"{num_b:>4} | {val_b}\n" if val_b or num_b else "\n"

                txt_a.insert(tk.END, line_a_fmt, type_a)
                txt_b.insert(tk.END, line_b_fmt, type_b)

            txt_a.config(state="disabled")
            txt_b.config(state="disabled")

    def _render_estadisticas(self):
        stats = self.diff_data.get('stats', {})
        archivos = self.diff_data.get('archivos_detalle', [])

        card_frame = ttk.Frame(self.diff_text, style='App.TFrame')
        card_frame.pack(fill="x", pady=(0, 15))

        metrics = [
            ("Archivos Modificados", str(stats.get('archivos_modificados', 0)), self.controller.colors["blue"]),
            ("Adiciones Totales (+)", f"+{stats.get('adiciones', 0)}", self.controller.colors["ok"]),
            ("Eliminaciones Totales (-)", f"-{stats.get('eliminaciones', 0)}", self.controller.colors["red"]),
            ("Archivos Nuevos", str(stats.get('archivos_nuevos', 0)), self.controller.colors["purple"])
        ]

        for title, val, color in metrics:
            card = ttk.Frame(card_frame, style='Panel.TFrame', padding=15)
            card.pack(side="left", fill="x", expand=True, padx=4)
            ttk.Label(card, text=title, font=("Segoe UI", 9), foreground=self.controller.colors["muted"], background=self.controller.colors["panel"]).pack()
            ttk.Label(card, text=val, font=("Segoe UI", 16, "bold"), foreground=color, background=self.controller.colors["panel"]).pack(pady=(4, 0))

        ttk.Label(self.diff_text, text="Desglose por Archivo", font=("Segoe UI", 11, "bold"), style='App.TLabel').pack(anchor="w", pady=(10, 5))

        cols = ("archivo", "estado", "adiciones", "eliminaciones")
        tree = ttk.Treeview(self.diff_text, columns=cols, show="headings", height=8)

        tree.heading("archivo", text="Nombre del Archivo")
        tree.heading("estado", text="Estado del Cambio")
        tree.heading("adiciones", text="Líneas Agregadas (+)")
        tree.heading("eliminaciones", text="Líneas Eliminadas (-)")

        tree.column("archivo", width=300)
        tree.column("estado", width=120)
        tree.column("adiciones", width=120)
        tree.column("eliminaciones", width=120)

        for a in archivos:
            tree.insert("", "end", values=(a['nombre'], a['estado'].capitalize(), f"+{a['adiciones']}", f"-{a['eliminaciones']}"))

        tree.pack(fill="both", expand=True)

class HU007_Ramas(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.ramas_lista = []
        self.chk_activa_var = tk.BooleanVar(value=False)

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.build_nav()
        
        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        top = ttk.Frame(content, style='App.TFrame')
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Gestión de Ramas", style='Title.TLabel').pack(side="left")
        ttk.Button(top, text="◀️ Volver al Panel", style='Primary.TButton', command=lambda: self.controller.show_frame("HU009_ListarRepositorios")).pack(side="right")
        ttk.Button(top, text="Sincronizar (Fetch)", style='Secondary.TButton', command=lambda: self.show_toast("Sincronización con remoto completada.", "info")).pack(side="right")

        repo = self.controller.proyecto_actual
        if not repo:
            ttk.Label(content, text="Selecciona un repositorio en el panel para gestionar sus ramas.", font=("Segoe UI", 11, "bold"), foreground=self.controller.colors["warn"], background=self.controller.colors["bg"]).pack(pady=40)
            return

        self.r_id = repo.id if hasattr(repo, 'id') else repo.get('id', 1)
        self.r_nombre = repo.nombre if hasattr(repo, 'nombre') else repo.get('nombre', 'Proyecto')

        # Tarjeta informativa del Repositorio
        info_frame = ttk.Frame(content, style='Panel.TFrame', padding=10)
        info_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(info_frame, text=f"📁 Repositorio: {self.r_nombre}", font=("Segoe UI", 10, "bold"), foreground=self.controller.colors["cyan"], background=self.controller.colors["panel"]).pack(side="left", padx=(0, 20))

        try:
            rama_activa = self.controller.facade.obtener_rama_activa(self.r_id)
            nombre_activa = rama_activa.get('nombre') if isinstance(rama_activa, dict) else getattr(rama_activa, 'nombre', 'main')
        except Exception:
            nombre_activa = "main"

        ttk.Label(info_frame, text=f"🌿 Rama Actual: {nombre_activa}", style='Chip.TLabel').pack(side="left")

        # Formulario para Crear Nueva Rama
        # Nueva Rama Form
        new_box = ttk.LabelFrame(content, text="Crear Nueva Rama")
        new_box.pack(fill="x", pady=10, ipady=10, ipadx=10)
        
        # Descripción añadida
        ttk.Label(new_box, text="Las ramas permiten trabajar en nuevas características, corregir errores o experimentar de forma aislada.", style='Help.TLabel').pack(anchor="w", pady=(0, 10))
        
        form_line = ttk.Frame(new_box, style='Panel.TFrame')
        form_line.pack(fill="x")
        
        ttk.Label(form_line, text="Nombre:", style='Panel.TLabel').pack(side="left", padx=5)
        self.b_name = ttk.Entry(form_line, font=("Segoe UI", 10), width=60)
        self.b_name.pack(side="left", padx=5)
        
        ttk.Label(form_line, text="Basada en:", style='Panel.TLabel').pack(side="left", padx=5)
        self.b_base = ttk.Combobox(form_line, values=["main", "develop"], state="readonly", width=30)
        self.b_base.current(0)
        self.b_base.pack(side="left", padx=5)

        self.chk_activa = ttk.Checkbutton(
            form_line,
            text="Establecer como rama activa al crear",
            variable=self.chk_activa_var,
            style='TCheckbutton'
        )
        self.chk_activa.pack(side="left", padx=(0, 15))
        
        ttk.Button(form_line, text="Crear Rama", style='Primary.TButton', command=self.crear_nueva_rama).pack(side="left", padx=15)
        
        # Tabla de Ramas Existentes
        list_header = ttk.Frame(content, style='App.TFrame')
        list_header.pack(fill="x", pady=(5, 5))
        ttk.Label(list_header, text="Ramas del Proyecto", font=("Segoe UI", 11, "bold"), style='App.TLabel').pack(side="left")

        cols = ("id", "nombre", "estado", "fecha")
        self.tree = ttk.Treeview(content, columns=cols, show="headings", height=7, selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("nombre", text="Nombre de Rama")
        self.tree.heading("estado", text="Estado")
        self.tree.heading("fecha", text="Fecha de Creación")

        self.tree.column("id", width=60, anchor="center")
        self.tree.column("nombre", width=250)
        self.tree.column("estado", width=150, anchor="center")
        self.tree.column("fecha", width=200, anchor="center")

        v_sc = ttk.Scrollbar(content, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=v_sc.set)

        self.tree.pack(side="top", fill="both", expand=True)

        # Barra de Acciones para la Rama Seleccionada
        action_bar = ttk.Frame(content, style='Panel.TFrame', padding=10)
        action_bar.pack(fill="x", pady=(10, 0))

        ttk.Label(action_bar, text="Acciones para la rama seleccionada:", style='Panel.TLabel').pack(side="left", padx=(0, 10))

        self.btn_activar = ttk.Button(
            action_bar,
            text="⭐ Establecer como Rama Activa",
            style='Primary.TButton',
            command=self.activar_rama_seleccionada
        )
        self.btn_activar.pack(side="left", padx=5)

        self.cargar_ramas()

    def cargar_ramas(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.ramas_lista = self.controller.facade.obtener_ramas_proyecto(self.r_id)
        except Exception:
            self.ramas_lista = []

        if not self.ramas_lista:
            self.ramas_lista = [{'id': 1, 'nombre': 'main', 'activa': 1, 'fecha_creacion': None}]

        for r in self.ramas_lista:
            r_id = r.get('id') if isinstance(r, dict) else getattr(r, 'id', '-')
            r_nombre = r.get('nombre') if isinstance(r, dict) else getattr(r, 'nombre', '-')
            es_activa = r.get('activa') if isinstance(r, dict) else getattr(r, 'activa', 0)
            f_creacion = r.get('fecha_creacion') if isinstance(r, dict) else getattr(r, 'fecha_creacion', None)

            estado_str = "🟢 ACTIVA (Actual)" if es_activa == 'Si' else "⚪ Inactiva"
            fecha_str = formatear_fecha_relativa(f_creacion) if f_creacion else "-"

            self.tree.insert("", "end", iid=str(r_id), values=(r_id, f"🌿 {r_nombre}", estado_str, fecha_str))

    def crear_nueva_rama(self):
        nombre = self.b_name.get().strip()
        hacer_activa = self.chk_activa_var.get()
        var_activa = ""

        if hacer_activa:
            var_activa = 'Si'
        else:
            var_activa = 'No'


        if not nombre:
            #self.show_toast("Por favor, ingresa un nombre para la nueva rama.", "warn")
            return

        try:
            res = self.controller.facade.crear_rama(
                id_proyecto=self.r_id,
                nombre_rama=nombre,
                id_version_base=None,
                activa=var_activa
            )
            if res:
                #self.show_toast(f"✓ Rama '{nombre}' creada exitosamente.", "success")
                self.b_name.delete(0, 'end')
                self.chk_activa_var.set(False)
                self.on_show()
            else:
                print("No se pudo crear la rama.")
                #self.show_toast("No se pudo crear la rama.", "error")
        except Exception as e:
            print(f"Error: {e}")
            #self.show_toast(f"Error: {e}", "error")

    def activar_rama_seleccionada(self):
        selected = self.tree.selection()
        if not selected:
            self.show_toast("Selecciona una rama de la lista para establecerla como activa.", "warn")
            return

        id_rama = selected[0]

        rama_obj = next((r for r in self.ramas_lista if str(r.get('id') if isinstance(r, dict) else getattr(r, 'id', '')) == str(id_rama)), None)

        if not rama_obj:
            return

        nombre_rama = rama_obj.get('nombre') if isinstance(rama_obj, dict) else getattr(rama_obj, 'nombre', '')
        es_activa = rama_obj.get('activa') if isinstance(rama_obj, dict) else getattr(rama_obj, 'activa', 0)

        if es_activa == 'Si':
            print(f"La rama '{nombre_rama}' ya es la rama activa del proyecto.")
            #self.show_toast(f"La rama '{nombre_rama}' ya es la rama activa del proyecto.", "warn")
            return

        try:
            self.controller.facade.cambiar_rama_activa(self.r_id, id_rama)
            #self.show_toast(f"✓ La rama '{nombre_rama}' es ahora la rama activa.", "success")
            self.on_show()
        except Exception as e:
            print(f"Error al activar la rama: {e}")
            #self.show_toast(f"Error al activar la rama: {e}", "error")

class HU008_Merge(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        
        box = ttk.Frame(self, style='Panel.TFrame', padding=30)
        box.pack(pady=20, fill="x", padx=40)
        
        header = ttk.Frame(box, style='Panel.TFrame')
        header.pack(fill="x")
        ttk.Label(header, text="Pull Request #42: Fix Autenticación Token", style='PanelTitle.TLabel').pack(side="left")
        ttk.Label(header, text="Abierto", style='Success.TLabel', background=self.controller.colors["panel_2"]).pack(side="left", padx=15)
        ttk.Label(header, text="Sin conflictos", style='Success.TLabel', background=self.controller.colors["panel_2"]).pack(side="left")
        
        ttk.Label(box, text="feature/login → main", foreground=self.controller.colors["cyan"], background=self.controller.colors["panel"], font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=10)
        
        # Descripción
        ttk.Label(box, text="Descripción del PR:", font=("Segoe UI", 10, "bold"), background=self.controller.colors["panel"], foreground=self.controller.colors["text"]).pack(anchor="w")
        ttk.Label(box, text="Se corrige el bug donde los usuarios no podían refrescar el JWT. Se agregan pruebas unitarias correspondientes.", style='Panel.TLabel', wraplength=800).pack(anchor="w", pady=(2, 15))
        
        # Listas de Meta Datos (Revisores, Archivos, Commits)
        info_frame = ttk.Frame(box, style='Panel.TFrame')
        info_frame.pack(fill="x", pady=10)
        
        ttk.Label(info_frame, text="👥 Revisores:", style='Help.TLabel').grid(row=0, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text="Admin (✅ Aprobado), QA (⏳ Pendiente)", style='Panel.TLabel').grid(row=0, column=1, sticky="w", padx=10, pady=2)
        
        ttk.Label(info_frame, text="📁 Archivos Modificados:", style='Help.TLabel').grid(row=1, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text="src/auth.py, tests/test_auth.py", style='Panel.TLabel').grid(row=1, column=1, sticky="w", padx=10, pady=2)
        
        ttk.Label(info_frame, text="📦 Commits Involucrados:", style='Help.TLabel').grid(row=2, column=0, sticky="w", pady=2)
        ttk.Label(info_frame, text="[a1b2c3d] Fix bug login, [e5f6g7h] Add auth tests", style='Panel.TLabel').grid(row=2, column=1, sticky="w", padx=10, pady=2)
        
        ttk.Label(box, text="Commits del Pull Request", font=("Segoe UI", 10, "bold"), background=self.controller.colors["panel"], foreground=self.controller.colors["text"]).pack(anchor="w", pady=(10, 5))
        commits_tree = ttk.Treeview(box, columns=("Hash", "Mensaje", "Autor"), show="headings", height=2)
        commits_tree.heading("Hash", text="Hash")
        commits_tree.heading("Mensaje", text="Mensaje")
        commits_tree.heading("Autor", text="Autor")
        commits_tree.column("Hash", width=80)
        commits_tree.insert("", "end", values=("a1b2c3d", "Fix bug login en JWT", "Juan Pérez"))
        commits_tree.insert("", "end", values=("e5f6g7h", "Add auth tests", "Juan Pérez"))
        commits_tree.pack(fill="x", pady=(0, 10))

        ttk.Label(box, text="Diff Destacados", font=("Segoe UI", 10, "bold"), background=self.controller.colors["panel"], foreground=self.controller.colors["text"]).pack(anchor="w", pady=(5, 5))
        diff_destacado = tk.Text(box, height=4, bg=self.controller.colors["panel_2"], fg=self.controller.colors["text"], font=("Consolas", 10), bd=1, relief="solid")
        diff_destacado.pack(fill="x", pady=(0, 10))
        diff_destacado.insert("1.0", "@@ -45,3 +45,4 @@\n def refresh_token():\n-    return None\n+    return create_new_token()\n+    # Validated")
        diff_destacado.tag_add("del", "3.0", "3.end")
        diff_destacado.tag_add("add", "4.0", "5.end")
        diff_destacado.tag_config("del", foreground=self.controller.colors["red"])
        diff_destacado.tag_config("add", foreground=self.controller.colors["ok"])
        diff_destacado.config(state="disabled")
        
        # Acciones
        btns = ttk.Frame(box, style='Panel.TFrame')
        btns.pack(fill="x", pady=25)
        
        ttk.Button(btns, text="✅ Aprobar PR", style='Primary.TButton', command=lambda: self.show_toast("Aprobación registrada.", "success")).pack(side="left", padx=2)
        ttk.Button(btns, text="⚠️ Solicitar Cambios", style='Secondary.TButton', command=lambda: self.show_toast("Cambios solicitados enviados al autor.", "warn")).pack(side="left", padx=2)
        ttk.Button(btns, text="💬 Comentar", style='Secondary.TButton', command=lambda: self.show_toast("Comentario agregado exitosamente.", "info")).pack(side="left", padx=2)
        
        ttk.Button(btns, text="Cerrar PR", style='Danger.TButton', command=lambda: self.show_toast("PR cerrado y rechazado.", "error")).pack(side="right", padx=2)
        ttk.Button(btns, text="🔀 Merge PR", style='Primary.TButton', command=lambda: self.show_toast("Merge (Squash) completado con éxito.", "success")).pack(side="right", padx=10)

class HU010_EliminarRepo(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)

    def on_show(self):
        for widget in self.winfo_children():
            widget.destroy()

        
        box = ttk.Frame(self, style='Panel.TFrame', padding=30)
        box.pack(pady=40, fill="x", padx=40)

        repo = self.controller.proyecto_actual
        if not repo:
            ttk.Label(box, text="⚠️ No hay ningún repositorio seleccionado.", font=("Segoe UI", 12, "bold"), foreground=self.controller.colors["warn"], background=self.controller.colors["panel"]).pack(pady=20)
            ttk.Button(box, text="Volver al Listado de Repositorios", style="Primary.TButton", command=lambda: self.controller.show_frame("HU009_ListarRepositorios")).pack()
            return

        self.r_id = repo.get("id") if isinstance(repo, dict) else getattr(repo, "id", 1)
        self.r_nombre = repo.get("nombre") if isinstance(repo, dict) else getattr(repo, "nombre", "Repositorio")
        self.r_ruta = repo.get("ruta", "") if isinstance(repo, dict) else getattr(repo, "ruta", "")
        self.rama_act = self.controller.facade.obtener_rama_activa(self.r_id)
        
        # Opciones extra de Backup antes del peligro
        safe_zone = ttk.Frame(box, style='Panel.TFrame')
        safe_zone.pack(fill="x", pady=(0, 20))
        ttk.Label(safe_zone, text="Opciones de Respaldo", style='PanelTitle.TLabel').pack(anchor="w")
        ttk.Label(safe_zone, text="Antes de eliminar, considera descargar una copia local o archivar el repositorio (solo lectura).", style='Panel.TLabel').pack(anchor="w", pady=5)
        
        s_btns = ttk.Frame(safe_zone, style='Panel.TFrame')
        s_btns.pack(anchor="w", pady=5)
        ttk.Button(s_btns, text="📥 Descargar ZIP", style='Secondary.TButton', command=lambda: self.show_toast("Descargando código fuente en ZIP...", "info")).pack(side="left", padx=(0, 5))
        ttk.Button(s_btns, text="📦 Archivar Repositorio", style='Secondary.TButton', command=lambda: self.show_toast("Repositorio archivado. Ahora es de solo lectura.", "warn")).pack(side="left")
        
        ttk.Separator(box, orient="horizontal").pack(fill="x", pady=15)
        
        # Zona de Peligro
        ttk.Label(box, text="Zona de Peligro", font=("Segoe UI", 16, "bold"), foreground=self.controller.colors["red"], background=self.controller.colors["panel"]).pack(anchor="w")
        
        ttk.Label(box, text=f"Repositorio a eliminar: '{self.r_nombre}'", font=("Segoe UI", 11, "bold"), foreground=self.controller.colors["text"], background=self.controller.colors["panel"]).pack(anchor="w", pady=(10, 5))
        
        ttk.Label(box, text=f"Rama actual: {self.rama_act.nombre}", style='Chip.TLabel').pack(anchor="w", pady=5)
        ttk.Label(box, text="Esta acción es irreversible. Se eliminará el código de todas las ramas, el historial de commits y las configuraciones.", style='Panel.TLabel').pack(anchor="w", pady=5)
        ttk.Label(box, text=f"Para confirmar, escribe: {self.r_nombre}", font=("Segoe UI", 10, "bold"), background=self.controller.colors["panel"], foreground=self.controller.colors["text"]).pack(anchor="w", pady=15)
        
        self.confirm_entry = ttk.Entry(box, font=("Segoe UI", 11))
        self.confirm_entry.pack(fill="x", pady=5)
        self.confirm_entry.bind("<KeyRelease>", self.validar_confirmacion)

        btn_box = ttk.Frame(box, style='Panel.TFrame')
        btn_box.pack(fill="x")
        
        self.del_btn = ttk.Button(btn_box, text="Eliminar Definitivamente", style='Danger.TButton', command=self.confirmar_eliminacion, state="disabled")
        self.del_btn.pack(side="left", padx=(0, 10))

        ttk.Button(
            btn_box, 
            text="Cancelar", 
            style="Secondary.TButton", 
            command=lambda: self.controller.show_frame("HU009_ListarRepositorios")
        ).pack(side="left")
        
    def validar_confirmacion(self, event=None):
        if self.confirm_entry.get().strip() == self.r_nombre:
            self.del_btn.config(state="normal")
        else:
            self.del_btn.config(state="disabled")

    def confirmar_eliminacion(self):
        try:
            self.controller.facade.eliminar_proyecto(self.r_id)
            self.controller.set_proyecto_actual(None)
            #self.show_toast(f"✓ El repositorio '{self.r_nombre}' ha sido eliminado.", "success")
            self.controller.show_frame("HU009_ListarRepositorios")
        except Exception as e:
            pass
            #self.show_toast(f"Error al eliminar repositorio: {e}", "error")

# Ejecución
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()