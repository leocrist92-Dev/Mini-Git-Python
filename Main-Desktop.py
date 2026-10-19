import tkinter as tk
from tkinter import ttk, messagebox
import re

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
            "border": "#1e293b" # Aproximación a rgba(255,255,255,.14)
        }
        
        self.configure(bg=self.colors["bg"])
        self.eval('tk::PlaceWindow . center')
        
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
        self.login_btn.config(text="Verificando...", state="disabled")
        self.show_toast("Validando credenciales contra el servicio de autenticación...", "info")
        self.after(1600, self.validate_login)
        
    def validate_login(self):
        if self.pass_input.get() == "ContraseñaIncorrecta":
            self.show_toast("✗ Usuario o contraseña inválida.", "error")
            self.login_btn.config(text="Ingresar", state="normal")
        else:
            self.show_toast("✓ Login exitoso.", "success")
            self.user_input.delete(0, 'end')
            self.pass_input.delete(0, 'end')
            self.login_btn.config(text="Ingresar")
            self.controller.show_frame("HU009_ListarRepositorios")
            
    def recover_pass(self):
        self.show_toast("✓ Enlace enviado. Revisa tu bandeja de entrada.", "success")

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
        self.show_toast("✓ Cuenta creada. Se envió correo de confirmación.", "success")
        for ent in self.inputs.values(): ent.delete(0, 'end')
        for lbl in self.helps.values(): lbl.config(text="")
        self.terms_var.set(False)

class HU009_ListarRepositorios(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        
        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        # Top Bar
        top_bar = ttk.Frame(content, style='App.TFrame')
        top_bar.pack(fill="x", pady=(0, 10))
        ttk.Label(top_bar, text="Mis Repositorios", style='Title.TLabel').pack(side="left")
        ttk.Button(top_bar, text="+ Nuevo Repositorio", style='Primary.TButton', command=lambda: controller.show_frame("HU003_CrearRepo")).pack(side="right")
        
        stats_frame = ttk.Frame(content, style='App.TFrame')
        stats_frame.pack(fill="x", pady=(0, 20))
        
        stats = [("Total Repos", "12", self.controller.colors["blue"]), 
                 ("Privados", "8", self.controller.colors["purple"]), 
                 ("Públicos", "4", self.controller.colors["ok"]), 
                 ("Commits Totales", "1,245", self.controller.colors["cyan"])]
                 
        for title, val, color in stats:
            card = ttk.Frame(stats_frame, style='Panel.TFrame')
            card.pack(side="left", fill="x", expand=True, padx=5, ipady=10)
            ttk.Label(card, text=title, font=("Segoe UI", 9), foreground=self.controller.colors["muted"], background=self.controller.colors["panel"]).pack(anchor="center")
            ttk.Label(card, text=val, font=("Segoe UI", 16, "bold"), foreground=color, background=self.controller.colors["panel"]).pack(anchor="center")
        
        filters = ttk.Frame(content, style='App.TFrame')
        filters.pack(fill="x", pady=(0, 15))
        
        self.search = ttk.Entry(filters, font=("Segoe UI", 10))
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.search.insert(0, "Buscar repositorios...")
        
        ttk.Label(filters, text="Privacidad:", style='App.TLabel').pack(side="left", padx=5)
        self.privacy_filter = ttk.Combobox(filters, values=["Todos", "Público", "Privado"], state="readonly", width=10)
        self.privacy_filter.current(0)
        self.privacy_filter.pack(side="left", padx=5)
        
        ttk.Button(filters, text="Tarjetas", style='Secondary.TButton', command=self.show_cards).pack(side="left", padx=2)
        ttk.Button(filters, text="Tabla", style='Secondary.TButton', command=self.show_table).pack(side="left", padx=2)
        
        # Contenedores de Vistas
        self.cards_frame = ttk.Frame(content, style='App.TFrame')
        self.table_frame = ttk.Frame(content, style='App.TFrame')
        
        self.repos = [("mi-proyecto-python", "Público", "Python", "Hace 2 horas"), 
                      ("api-backend", "Privado", "JavaScript", "Ayer"), 
                      ("portafolio-web", "Público", "HTML/CSS", "Hace 3 días")]
        
        self.build_cards()
        self.build_table()
        self.show_cards()

    def build_cards(self):
        for widget in self.cards_frame.winfo_children(): widget.destroy()
        for name, priv, lang, time in self.repos:
            card = ttk.Frame(self.cards_frame, style='Panel.TFrame')
            card.pack(fill="x", pady=5, ipady=10, ipadx=10)
            
            # Info izquierda
            info_frame = ttk.Frame(card, style='Panel.TFrame')
            info_frame.pack(side="left", fill="y")
            ttk.Label(info_frame, text=name, font=("Segoe UI", 12, "bold"), foreground=self.controller.colors["blue"], background=self.controller.colors["panel"]).pack(side="left", padx=(0, 10))
            ttk.Label(info_frame, text=priv, style='Chip.TLabel').pack(side="left", padx=5)
            ttk.Label(info_frame, text=lang, style='Panel.TLabel').pack(side="left", padx=5)
            ttk.Label(info_frame, text=time, style='Help.TLabel').pack(side="left", padx=10)
            
            # Botones derecha
            action_frame = ttk.Frame(card, style='Panel.TFrame')
            action_frame.pack(side="right")
            ttk.Button(action_frame, text="Commits", style='Secondary.TButton', command=lambda: self.controller.show_frame("HU005_Historial")).pack(side="left", padx=2)
            ttk.Button(action_frame, text="Ramas", style='Secondary.TButton', command=lambda: self.controller.show_frame("HU007_Ramas")).pack(side="left", padx=2)
            ttk.Button(action_frame, text="Eliminar", style='Danger.TButton', command=lambda: self.controller.show_frame("HU010_EliminarRepo")).pack(side="left", padx=2)

    def build_table(self):
        cols = ("Nombre", "Privacidad", "Lenguaje", "Actualizado")
        self.tree = ttk.Treeview(self.table_frame, columns=cols, show="headings", height=8)
        for col in cols: self.tree.heading(col, text=col)
        for row in self.repos: self.tree.insert("", "end", values=row)
        self.tree.pack(fill="both", expand=True)

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
        
    def validate(self, event=None):
        name = self.name_input.get().strip()
        if re.match(r"^[a-zA-Z0-9-]{3,50}$", name):
            self.btn.config(state="normal")
            self.help_lbl.config(text="✓ Nombre disponible", style='Success.TLabel')
        else:
            self.btn.config(state="disabled")
            self.help_lbl.config(text="⚠️ Usa 3-50 caracteres con letras, números o guion", style='Help.TLabel')
            
    def create_repo(self):
        self.show_toast("✓ Repositorio creado exitosamente.", "success")
        self.name_input.delete(0, 'end')
        self.desc_input.delete(0, 'end')
        self.btn.config(state="disabled")

class HU004_Commit(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        
        box = ttk.Frame(self, style='App.TFrame', padding=20)
        box.pack(fill="both", expand=True)
        
        top = ttk.Frame(box, style='App.TFrame')
        top.pack(fill="x")
        ttk.Label(top, text="Cambios Pendientes (Staging)", style='Title.TLabel').pack(side="left")
        ttk.Button(top, text="Ocultar/Mostrar Diff", style='Secondary.TButton', command=self.toggle_diff).pack(side="right")
        
        # Etiquetas (Autor, Rama, Fecha)
        meta_frame = ttk.Frame(box, style='App.TFrame')
        meta_frame.pack(fill="x", pady=10)
        ttk.Label(meta_frame, text="👤 Autor: Juan Pérez", style='Chip.TLabel').pack(side="left", padx=2)
        ttk.Label(meta_frame, text="🌿 Rama: feature/login", style='Chip.TLabel').pack(side="left", padx=2)
        ttk.Label(meta_frame, text="📅 Fecha: Ahora mismo", style='Chip.TLabel').pack(side="left", padx=2)
        
        self.diff_visible = True
        self.diff_frame = ttk.Frame(box, style='Panel.TFrame')
        self.diff_frame.pack(fill="x", pady=(5, 15))
        
        self.diff = tk.Text(self.diff_frame, height=6, bg=self.controller.colors["panel"], fg=self.controller.colors["cyan"], font=("Consolas", 10), bd=1, relief="solid")
        self.diff.pack(fill="x", padx=2, pady=2)
        self.diff.insert("1.0", "--- a/main.py\n+++ b/main.py\n@@ -1,3 +1,4 @@\n def saludar():\n-    print('Hola')\n+    print('Hola Mundo')\n+    print('SENA')")
        
        self.diff.tag_add("del", "5.0", "5.end")
        self.diff.tag_add("add", "6.0", "7.end")
        self.diff.tag_config("del", foreground=self.controller.colors["red"])
        self.diff.tag_config("add", foreground=self.controller.colors["ok"])
        
        self.diff.config(state="disabled")
        
        ttk.Label(box, text="Mensaje del Commit (Corto) *", style='App.TLabel').pack(anchor="w")
        self.msg = ttk.Entry(box, font=("Segoe UI", 11))
        self.msg.pack(fill="x", pady=5)
        self.msg.bind("<KeyRelease>", self.check)
        
        ttk.Label(box, text="Descripción Detallada (Opcional)", style='App.TLabel').pack(anchor="w", pady=(10, 0))
        self.desc = tk.Text(box, height=4, bg=self.controller.colors["panel_2"], fg="white", font=("Segoe UI", 10), bd=1, relief="solid")
        self.desc.pack(fill="x", pady=5)
        
        btns = ttk.Frame(box, style='App.TFrame')
        btns.pack(fill="x", pady=10)
        
        self.btn_save = ttk.Button(btns, text="Guardar Commit", style='Primary.TButton', command=self.save_commit, state="disabled")
        self.btn_save.pack(side="left")
        ttk.Button(btns, text="Descartar Cambios", style='Danger.TButton', command=self.discard).pack(side="right")

    def toggle_diff(self):
        if self.diff_visible:
            self.diff_frame.pack_forget()
        else:
            # Se reinserta antes del mensaje corto
            self.diff_frame.pack(fill="x", pady=(5, 15), before=self.msg.master.winfo_children()[4]) 
        self.diff_visible = not self.diff_visible
        
    def check(self, event=None):
        self.btn_save.config(state="normal" if self.msg.get().strip() else "disabled")
        
    def save_commit(self):
        self.show_toast("✓ Commit guardado exitosamente. Hash: a1b2c3d4e5f6", "success")
        self.msg.delete(0, 'end')
        self.desc.delete("1.0", "end")
        self.btn_save.config(state="disabled")
        
    def discard(self):
        self.show_toast("Cambios descartados. Ya no hay archivos pendientes.", "error")
        self.msg.delete(0, 'end')
        self.desc.delete("1.0", "end")

class HU005_Historial(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        
        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        ttk.Label(content, text="Historial de Commits", style='Title.TLabel').pack(anchor="w", pady=(0, 10))
        
        # Tarjetas Estadísticas Superiores
        stats_frame = ttk.Frame(content, style='App.TFrame')
        stats_frame.pack(fill="x", pady=(0, 15))
        
        stats = [("Total Commits", "345", self.controller.colors["blue"]), 
                 ("Autores", "4", self.controller.colors["purple"]), 
                 ("Días Activos", "120", self.controller.colors["ok"]), 
                 ("Líneas Modificadas", "+4.5k / -1.2k", self.controller.colors["warn"])]
                 
        for title, val, color in stats:
            card = ttk.Frame(stats_frame, style='Panel.TFrame')
            card.pack(side="left", fill="x", expand=True, padx=5, ipady=5)
            ttk.Label(card, text=title, font=("Segoe UI", 8), foreground=self.controller.colors["muted"], background=self.controller.colors["panel"]).pack(anchor="center")
            ttk.Label(card, text=val, font=("Segoe UI", 12, "bold"), foreground=color, background=self.controller.colors["panel"]).pack(anchor="center")
        
        filters = ttk.Frame(content, style='App.TFrame')
        filters.pack(fill="x", pady=5)
        
        ttk.Label(filters, text="Autor:", style='App.TLabel').pack(side="left")
        self.author = ttk.Combobox(filters, values=["Todos", "Juan Pérez", "Admin"], state="readonly", width=15)
        self.author.current(0)
        self.author.pack(side="left", padx=5)
        
        self.search = ttk.Entry(filters, font=("Segoe UI", 10))
        self.search.pack(side="left", fill="x", expand=True, padx=5)
        self.search.insert(0, "Buscar en commits...")
        
        paned = ttk.PanedWindow(content, orient="horizontal")
        paned.pack(fill="both", expand=True, pady=10)
        
        # Lista
        cols = ("Hash", "Mensaje", "Autor", "Fecha")
        self.tree = ttk.Treeview(paned, columns=cols, show="headings")
        for c in cols: self.tree.heading(c, text=c)
        self.tree.column("Hash", width=80)
        self.tree.insert("", "end", values=("a1b2c3d", "Fix error login e implementación de tokens", "Juan Pérez", "Hace 10 min"))
        self.tree.insert("", "end", values=("f6e5d4c", "Actualización README y docs", "Admin", "Ayer"))
        self.tree.bind("<<TreeviewSelect>>", self.show_detail)
        paned.add(self.tree, weight=2)
        
        # Detalle
        self.detail = tk.Text(paned, bg=self.controller.colors["panel"], fg=self.controller.colors["text"], font=("Segoe UI", 10), state="disabled", wrap="word")
        paned.add(self.detail, weight=1)

    def show_detail(self, event):
        item = self.tree.selection()
        if not item: return
        val = self.tree.item(item[0], "values")
        self.detail.config(state="normal")
        self.detail.delete("1.0", "end")
        self.detail.insert("end", f"Hash: {val[0]}\nRama: main\nAutor: {val[2]}\nFecha: {val[3]}\n\nMensaje:\n{val[1]}\n\n--- ARCHIVOS MODIFICADOS ---\n* src/auth.py (+15, -2)\n* config.json (+1, -0)\n\n--- DIFF Simulada ---\n+ Código agregado\n- Código eliminado")
        self.detail.config(state="disabled")

class HU006_Diff(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        
        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        ttk.Label(content, text="Repositorio: mi-proyecto-python", font=("Segoe UI", 10, "bold"), foreground=self.controller.colors["muted"], background=self.controller.colors["bg"]).pack(anchor="w")
        
        top = ttk.Frame(content, style='App.TFrame')
        top.pack(fill="x", pady=(5, 10))
        ttk.Label(top, text="Comparar Versiones (Diff)", style='Title.TLabel').pack(side="left")
        
        # Selectores de Commits / Ramas
        select_frame = ttk.Frame(content, style='App.TFrame')
        select_frame.pack(fill="x", pady=5)
        
        ttk.Label(select_frame, text="Base:", style='App.TLabel').pack(side="left")
        self.c_base = ttk.Combobox(select_frame, values=["main", "v1.0", "a1b2c3d (Ayer)"], state="readonly", width=15)
        self.c_base.current(0)
        self.c_base.pack(side="left", padx=5)
        
        ttk.Label(select_frame, text="vs  Comparar con:", style='App.TLabel').pack(side="left", padx=10)
        self.c_comp = ttk.Combobox(select_frame, values=["feature/login", "v1.1", "f6e5d4c (Hoy)"], state="readonly", width=15)
        self.c_comp.current(0)
        self.c_comp.pack(side="left", padx=5)
        
        ttk.Button(select_frame, text="Comparar", style='Primary.TButton', command=self.do_compare).pack(side="left", padx=15)
        
        tabs = ttk.Frame(content, style='App.TFrame')
        tabs.pack(fill="x", pady=10)
        ttk.Button(tabs, text="Unificado", style='Secondary.TButton', command=lambda: self.switch_tab("uni")).pack(side="left", padx=2)
        ttk.Button(tabs, text="Lado a Lado", style='Secondary.TButton', command=lambda: self.switch_tab("side")).pack(side="left", padx=2)
        ttk.Button(tabs, text="Estadísticas", style='Secondary.TButton', command=lambda: self.switch_tab("stats")).pack(side="left", padx=2)
        
        actions = ttk.Frame(tabs, style='App.TFrame')
        actions.pack(side="right")
        ttk.Button(actions, text="Copiar Diff", style='Secondary.TButton', command=lambda: self.show_toast("✓ Copiado al portapapeles", "success")).pack(side="left", padx=2)
        
        self.diff_text = tk.Text(content, bg=self.controller.colors["panel"], fg=self.controller.colors["text"], font=("Consolas", 11))
        self.diff_text.pack(fill="both", expand=True)
        self.switch_tab("uni") # Carga inicial

    def do_compare(self):
        base = self.c_base.get()
        comp = self.c_comp.get()
        self.show_toast(f"Comparando {base} vs {comp}. Resultado: +12 líneas, -4 líneas.", "info")

    def switch_tab(self, mode):
        self.diff_text.config(state="normal")
        self.diff_text.delete("1.0", "end")
        if mode == "uni":
            self.diff_text.insert("end", "@@ -12,5 +12,6 @@\n def verificar():\n-    return False\n+    return True\n+    # Corregido por QA")
            self.diff_text.tag_add("del", "3.0", "3.end")
            self.diff_text.tag_add("add", "4.0", "5.end")
        elif mode == "side":
            self.diff_text.insert("end", "LADO IZQUIERDO (Base)          | LADO DERECHO (Comparar)\n--------------------------------------------------------\n def verificar():              |  def verificar():\n-    return False              | +    return True\n                               | +    # Corregido por QA")
            self.diff_text.tag_add("del", "4.0", "4.30")
            self.diff_text.tag_add("add", "4.33", "5.end")
        elif mode == "stats":
            self.diff_text.insert("end", "Estadísticas de la Comparación:\n-------------------------------\nArchivos modificados: 1\nInserciones (+): 2\nEliminaciones (-): 1\n\nDesglose por archivo:\n- src/auth.py: +2, -1")
            
        self.diff_text.tag_config("del", foreground=self.controller.colors["red"])
        self.diff_text.tag_config("add", foreground=self.controller.colors["ok"])
        self.diff_text.config(state="disabled")

class HU007_Ramas(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.build_nav()
        
        content = ttk.Frame(self, style='App.TFrame', padding=20)
        content.pack(fill="both", expand=True)
        
        top = ttk.Frame(content, style='App.TFrame')
        top.pack(fill="x", pady=(0, 10))
        ttk.Label(top, text="Gestión de Ramas", style='Title.TLabel').pack(side="left")
        ttk.Button(top, text="Sincronizar (Fetch)", style='Secondary.TButton', command=lambda: self.show_toast("Sincronización con remoto completada.", "info")).pack(side="right")
        
        # Nueva Rama Form
        new_box = ttk.LabelFrame(content, text="Crear Nueva Rama")
        new_box.pack(fill="x", pady=10, ipady=10, ipadx=10)
        
        # Descripción añadida
        ttk.Label(new_box, text="Las ramas permiten trabajar en nuevas características, corregir errores o experimentar de forma aislada.", style='Help.TLabel').pack(anchor="w", pady=(0, 10))
        
        form_line = ttk.Frame(new_box, style='Panel.TFrame')
        form_line.pack(fill="x")
        
        ttk.Label(form_line, text="Nombre:", style='Panel.TLabel').pack(side="left", padx=5)
        self.b_name = ttk.Entry(form_line, font=("Segoe UI", 10))
        self.b_name.pack(side="left", padx=5)
        
        ttk.Label(form_line, text="Basada en:", style='Panel.TLabel').pack(side="left", padx=5)
        self.b_base = ttk.Combobox(form_line, values=["main", "develop"], state="readonly", width=10)
        self.b_base.current(0)
        self.b_base.pack(side="left", padx=5)
        
        ttk.Button(form_line, text="Crear Rama", style='Primary.TButton', command=self.new_branch).pack(side="left", padx=15)
        
        # Lista de Ramas
        self.tree = ttk.Treeview(content, columns=("Rama", "Estado", "Último Commit"), show="headings", height=8)
        self.tree.heading("Rama", text="Nombre de Rama")
        self.tree.heading("Estado", text="Estado")
        self.tree.heading("Último Commit", text="Último Commit")
        self.tree.insert("", "end", values=("🌿 main", "Activa", "Hace 2 horas (a1b2c3d)"))
        self.tree.insert("", "end", values=("feature/login", "Desactualizada", "Ayer (f6e5d4c)"))
        self.tree.pack(fill="both", expand=True, pady=10)
        
        ttk.Button(content, text="Cambiar a Rama Seleccionada (Checkout)", style='Secondary.TButton', command=lambda: self.show_toast("Checkout exitoso. Rama actual cambiada.", "success")).pack()

    def new_branch(self):
        name = self.b_name.get().strip()
        if name:
            self.show_toast(f"✓ Rama '{name}' creada exitosamente basada en {self.b_base.get()}.", "success")
            self.tree.insert("", "end", values=(f"🌿 {name}", "Nueva / Activa", "Justo ahora"))
            self.b_name.delete(0, 'end')

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
        self.build_nav()
        
        box = ttk.Frame(self, style='Panel.TFrame', padding=30)
        box.pack(pady=40, fill="x", padx=40)
        
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
        
        ttk.Label(box, text="Repositorio a eliminar: mi-proyecto-python", font=("Segoe UI", 11, "bold"), foreground=self.controller.colors["text"], background=self.controller.colors["panel"]).pack(anchor="w", pady=(10, 5))
        
        ttk.Label(box, text="Rama actual: main", style='Chip.TLabel').pack(anchor="w", pady=5)
        ttk.Label(box, text="Esta acción es irreversible. Se eliminará el código de todas las ramas, el historial de commits y las configuraciones.", style='Panel.TLabel').pack(anchor="w", pady=5)
        ttk.Label(box, text="Para confirmar, escribe: mi-proyecto-python", font=("Segoe UI", 10, "bold"), background=self.controller.colors["panel"], foreground=self.controller.colors["text"]).pack(anchor="w", pady=15)
        
        self.confirm = ttk.Entry(box, font=("Segoe UI", 11))
        self.confirm.pack(fill="x", pady=5)
        self.confirm.bind("<KeyRelease>", self.check)
        
        self.del_btn = ttk.Button(box, text="Eliminar Definitivamente", style='Danger.TButton', command=self.delete, state="disabled")
        self.del_btn.pack(fill="x", pady=15)
        
    def check(self, event=None):
        if self.confirm.get() == "mi-proyecto-python":
            self.del_btn.config(state="normal")
            self.show_toast("✓ Nombre de confirmación correcto.", "success")
        else:
            self.del_btn.config(state="disabled")
            
    def delete(self):
        if messagebox.askyesno("Seguridad Modal", "Estás a punto de eliminar permanentemente el repositorio.\n¿Estás completamente seguro?"):
            self.show_toast("✓ Repositorio eliminado de forma permanente. Auditoría registrada.", "error")
            self.confirm.delete(0, 'end')
            self.del_btn.config(state="disabled")

# Ejecución
if __name__ == "__main__":
    app = MainApp()
    app.mainloop()