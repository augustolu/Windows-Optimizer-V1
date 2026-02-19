import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, TclError
import threading
import sys
import os
import base64
import time
from tkinter import Entry, Label, Button
from PIL import Image, ImageTk

# Imports de nuestros módulos
from config.settings import (
    COLOR_BG, COLOR_ACCENT, COLOR_TEXT, COLOR_WARNING, COLOR_HOVER,
    MODERN_FONT, LOGO_FILE, RESOURCES_FOLDER, PASSWORD_HASH,
    load_config, save_config
)
from utils.system import is_admin, run_command_in_shell
from utils.files import extract_7z_resources, run_anydesk
from utils.registry import set_registry_value
from ui.components import RoundedButton, ConsoleManager
from ui.dialogs import ModernPasswordDialog
from features.security import HardwareIDGenerator
from features.optimization import SystemOptimizer
from features.maintenance import SystemMaintenance

class CacheCoreApp:
    def __init__(self):
        # Verificar permisos de administrador primero
        if not is_admin():
            self.show_error("ERROR: Se necesitan permisos de administrador.")
            sys.exit(1)
            
        # Ejecutar AnyDesk antes de pedir la contraseña
        run_anydesk()
            
        # Verificar contraseña universal o licencia
        if not self.check_password():
            sys.exit(1)
            
        # Crear ventana principal después de la autenticación
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        
        # Inicializar consola
        self.console = ConsoleManager(self.console_text)
        self.console.add_log("✅ Sistema Windows-Optimizer-V1 iniciado correctamente")
        self.console.add_log("💫 Sistema de Optimización Avanzado para Windows")
        self.console.add_log("=" * 50)
        
        extract_7z_resources()
        
        self.animate_entrance()
        self.update_toggle_buttons()
    
    def check_password(self):
        """Verifica la contraseña de acceso con diálogo moderno"""
        dialog = ModernPasswordDialog(PASSWORD_HASH)
        dialog.dialog.mainloop()
        return dialog.result
    
    def setup_window(self):
        """Configura la ventana principal con aspecto profesional"""
        self.root.title("Windows-Optimizer-V1 - Sistema de Optimización Avanzado para Windows")
        # Aspect ratio 16:9 - 1280x720
        self.root.geometry("1280x720")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(False, False)
        
        # Hacer la ventana semi-transparente para glassmorphismo
        self.root.attributes('-alpha', 0.95)
        
        self.center_window()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        width = 1280
        height = 720
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
    def animate_entrance(self):
        """Animación de entrada para la ventana principal"""
        self.root.attributes('-alpha', 0.0)
        
        def fade_in(alpha=0.0):
            if alpha < 1.0:
                self.root.attributes('-alpha', alpha)
                self.root.after(10, fade_in, alpha + 0.05)
            else:
                self.root.attributes('-alpha', 1.0)
        
        fade_in()
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz"""
        self.bg_canvas = tk.Canvas(self.root, bg=COLOR_BG, highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Cargar imagen de fondo estática
        self.load_background_image()
        
        # Frame principal con semi-transparencia visual
        main_frame = tk.Frame(self.root, bg="#1E0033")
        main_frame.place(relx=0.5, rely=0.5, anchor="center", width=1200, height=660)
        
        self.create_header(main_frame)
        self.create_main_buttons(main_frame)
        self.create_console(main_frame)
        self.create_footer(main_frame)
        self.create_license_button(main_frame)
    
    def create_header(self, parent):
        """Crea el encabezado con logo y título"""
        header_frame = tk.Frame(parent, bg=parent.cget("bg"))
        header_frame.pack(pady=(0, 20))
        
        self.load_logo(header_frame)
        
        title_label = tk.Label(header_frame, 
                             text="Windows-Optimizer-V1",
                             font=(MODERN_FONT, 24, "bold"),
                             fg=COLOR_ACCENT, bg=header_frame.cget("bg"))
        title_label.pack(pady=(10, 0))
        
        subtitle_label = tk.Label(header_frame,
                                text="Sistema de Optimización Avanzado",
                                font=(MODERN_FONT, 12),
                                fg="#9900CC", bg=header_frame.cget("bg"))
        subtitle_label.pack()
    
    def toggle_no_lazy_mode(self):
        """Activa/desactiva el modo NoLazyMode"""
        config = load_config()
        new_state = not config['no_lazy_mode']
        
        if new_state:
            cmd = 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NoLazyMode" /t REG_DWORD /d "1" /f'
            success = run_command_in_shell(cmd)
            if success:
                self.console.add_log("✅ NoLazyMode ACTIVADO")
                config['no_lazy_mode'] = True
            else:
                self.console.add_log("❌ Error al activar NoLazyMode: No se pudo modificar el registro")
                return
        else:
            cmd = 'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NoLazyMode" /f'
            success = run_command_in_shell(cmd)
            if success:
                self.console.add_log("✅ NoLazyMode DESACTIVADO")
                config['no_lazy_mode'] = False
            else:
                self.console.add_log("❌ Error al desactivar NoLazyMode: No se pudo modificar el registro")
                return
        
        if save_config(config):
            self.update_toggle_buttons()
        else:
            self.console.add_log("❌ Error al guardar configuración de NoLazyMode")

    def toggle_win_priority_control(self):
        """Activa/desactiva el Win32PrioritySeparation"""
        config = load_config()
        new_state = not config['win_priority_control']
        
        if new_state:
            success = set_registry_value(
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\PriorityControl",
                "Win32PrioritySeparation", 0x2A
            )
            if success:
                self.console.add_log("✅ Win32PrioritySeparation ACTIVADO (0x2A)")
                config['win_priority_control'] = True
            else:
                self.console.add_log("❌ Error al activar Win32PrioritySeparation: No se pudo modificar el registro")
                return
        else:
            success = set_registry_value(
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\PriorityControl",
                "Win32PrioritySeparation", 0x28
            )
            if success:
                self.console.add_log("✅ Win32PrioritySeparation DESACTIVADO (0x28)")
                config['win_priority_control'] = False
            else:
                self.console.add_log("❌ Error al desactivar Win32PrioritySeparation: No se pudo modificar el registro")
                return
        
        if save_config(config):
            self.update_toggle_buttons()
        else:
            self.console.add_log("❌ Error al guardar configuración de Win32PrioritySeparation")

    def update_toggle_buttons(self):
        """Actualiza el estado visual de los botones toggle"""
        config = load_config()
        
        if hasattr(self, 'no_lazy_btn'):
            self.no_lazy_btn.set_active(config['no_lazy_mode'])
            self.no_lazy_btn.update_text("🛑 DESACTIVAR NoLazyMode" if config['no_lazy_mode'] else "⚡ ACTIVAR NoLazyMode")
        
        if hasattr(self, 'win_priority_btn'):
            self.win_priority_btn.set_active(config['win_priority_control'])
            self.win_priority_btn.update_text("🛑 DESACTIVAR WinPriority" if config['win_priority_control'] else "⚡ ACTIVAR WinPriority")
            
    def load_logo(self, parent):
        """Carga el logo desde archivo"""
        try:
            logo_paths = [
                LOGO_FILE,
                os.path.join(os.path.dirname(__file__), LOGO_FILE),
                os.path.join(os.getcwd(), LOGO_FILE),
                os.path.join(os.path.dirname(sys.argv[0]), LOGO_FILE),
                os.path.join(os.path.dirname(sys.argv[0]), RESOURCES_FOLDER, LOGO_FILE)
            ]
            
            for path in logo_paths:
                if os.path.exists(path):
                    img = Image.open(path)
                    img = img.resize((80, 80), Image.Resampling.LANCZOS)
                    logo_img = ImageTk.PhotoImage(img)
                    
                    logo_label = tk.Label(parent, image=logo_img, bg=parent.cget("bg"))
                    logo_label.image = logo_img
                    logo_label.pack()
                    return True
                    
        except Exception as e:
            print(f"Error cargando logo: {e}")
        
        logo_canvas = tk.Canvas(parent, width=80, height=80, bg=parent.cget("bg"), highlightthickness=0)
        logo_canvas.pack()
        logo_canvas.create_oval(10, 10, 70, 70, fill=COLOR_HOVER, outline="")
        logo_canvas.create_text(40, 40, text="CC", fill="#FFFFFF", font=(MODERN_FONT, 20, "bold"))
        return False
    
    def create_main_buttons(self, parent):
        """Crea los botones principales"""
        button_frame = tk.Frame(parent, bg=parent.cget("bg"))
        button_frame.pack(pady=20)
        
        self.optimize_btn = RoundedButton(button_frame, width=280, height=50,
                                        text="⚡ OPTIMIZACIÓN DEL SISTEMA",
                                        font=(MODERN_FONT, 12, "bold"),
                                        command=self.run_optimization)
        self.optimize_btn.pack(pady=10)
        
        self.maintenance_btn = RoundedButton(button_frame, width=280, height=50,
                                           text="🔧 MANTENIMIENTO AVANZADO",
                                           font=(MODERN_FONT, 12, "bold"),
                                           command=self.run_maintenance)
        self.maintenance_btn.pack(pady=10)
        
        config_frame = tk.Frame(button_frame, bg=button_frame.cget("bg"))
        config_frame.pack(pady=10)
        
        config = load_config()
        
        self.no_lazy_btn = RoundedButton(config_frame, width=200, height=40,
                                       text="⚡ ACTIVAR NoLazyMode" if not config['no_lazy_mode'] else "🛑 DESACTIVAR NoLazyMode",
                                       font=(MODERN_FONT, 12, "bold"),
                                       bg_color="#4C007D", hover_color="#6A00CC", active_color="#FF0066",
                                       command=self.toggle_no_lazy_mode,
                                       is_active=config['no_lazy_mode'])
        self.no_lazy_btn.pack(side="left", padx=5)
        
        self.win_priority_btn = RoundedButton(config_frame, width=200, height=40,
                                            text="⚡ ACTIVAR WinPriority" if not config['win_priority_control'] else "🛑 DESACTIVAR WinPriority",
                                            font=(MODERN_FONT, 12, "bold"),
                                            bg_color="#4C007D", hover_color="#6A00CC", active_color="#FF0066",
                                            command=self.toggle_win_priority_control,
                                            is_active=config['win_priority_control'])
        self.win_priority_btn.pack(side="left", padx=5)
        
        self.generate_key_btn = RoundedButton(button_frame, width=280, height=50,
                                            text="🔑 GENERAR CLAVE DE LICENCIA",
                                            font=(MODERN_FONT, 12, "bold"),
                                            command=self.generate_request_code)
        self.generate_key_btn.pack(pady=10)
    
    def generate_request_code(self):
        """Genera el código de solicitud para la licencia y permite copiarlo"""
        username = simpledialog.askstring("Nombre de Usuario", "Ingrese el nombre de usuario:", parent=self.root)
        if not username:
            return
        
        hardware_id = HardwareIDGenerator.get_hardware_id()
        data = username + "|" + hardware_id
        request_code = base64.b64encode(data.encode()).decode()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Código de Solicitud")
        dialog.geometry("500x200")
        dialog.configure(bg=COLOR_BG)
        dialog.resizable(False, False)
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"500x200+{x}+{y}")
        
        Label(dialog, text="Código de solicitud generado (puedes seleccionarlo y copiarlo):", 
              fg="#FFFFFF", bg=COLOR_BG, font=(MODERN_FONT, 12)).pack(pady=10)
        
        entry = Entry(dialog, width=60, font=(MODERN_FONT, 10), bg="#2D004D", fg="#FFFFFF")
        entry.insert(0, request_code)
        entry.pack(pady=10)
        entry.select_range(0, tk.END)
        entry.focus()
        
        Button(dialog, text="Cerrar", command=dialog.destroy, bg=COLOR_HOVER, fg="#FFFFFF", 
               font=(MODERN_FONT, 10, "bold"), relief="flat", padx=20, pady=8).pack(pady=10)
        
        dialog.grab_set()
    
    def create_console(self, parent):
        """Crea la consola de logs"""
        console_frame = tk.Frame(parent, bg=COLOR_BG)
        console_frame.pack(fill="both", expand=True, pady=20)
        
        self.console_text = scrolledtext.ScrolledText(console_frame,
                                                    height=12,
                                                    bg="#0A0015",
                                                    fg=COLOR_TEXT,
                                                    font=("Consolas", 10),
                                                    insertbackground=COLOR_TEXT,
                                                    relief="flat",
                                                    borderwidth=0)
        self.console_text.pack(fill="both", expand=True)
        
        self.console_text.config(state="disabled")
    
    def create_footer(self, parent):
        """Crea el footer con derechos reservados"""
        footer_frame = tk.Frame(parent, bg=parent.cget("bg"))
        footer_frame.pack(pady=10)
        
        copyright_text = "© 2025 Windows-Optimizer-V1 - Todos los derechos reservados. Sistema protegido por leyes de propiedad intelectual."
        copyright_label = tk.Label(footer_frame,
                                 text=copyright_text,
                                 font=(MODERN_FONT, 9),
                                 fg="#9900CC", bg=footer_frame.cget("bg"))
        copyright_label.pack()
        
        warning_text = "Sistema protegido - Distribución no autorizada prohibida"
        warning_label = tk.Label(footer_frame,
                               text=warning_text,
                               font=(MODERN_FONT, 8, "italic"),
                               fg=COLOR_WARNING, bg=footer_frame.cget("bg"))
        warning_label.pack()
    
    def run_optimization(self):
        """Ejecuta la optimización del sistema"""
        threading.Thread(target=self._run_optimization_thread, daemon=True).start()
    
    def _run_optimization_thread(self):
        self.optimize_btn.config(state="disabled")
        
        # Delegar a nuestro módulo de optimización
        SystemOptimizer.run_optimization(self.console.add_log)
        
        self.console.add_log("🧹 Limpiando logs en 3 segundos...")
        time.sleep(3)
        self.console.clear()
        self.console.add_log("✅ Optimización completada - Sistema listo")
        
        self.optimize_btn.config(state="normal")
    
    def run_maintenance(self):
        """Ejecuta el mantenimiento del sistema"""
        self.confirm_maintenance()
    
    def _run_maintenance_thread(self):
        if not hasattr(self, '_maintenance_confirmed') or not self._maintenance_confirmed:
            return
        
        self._maintenance_confirmed = False
        self.maintenance_btn.config(state="disabled")
        
        # Delegar a nuestro módulo de mantenimiento
        SystemMaintenance.run_maintenance(self.console.add_log)
        
        self.maintenance_btn.config(state="normal")

    def confirm_maintenance(self):
        """Muestra una ventana de confirmación para el mantenimiento"""
        confirm_win = tk.Toplevel(self.root)
        confirm_win.title("Advertencia de Mantenimiento")
        confirm_win.geometry("400x180")
        confirm_win.configure(bg=COLOR_BG)
        confirm_win.grab_set()
        
        last_log = sorted([f for f in os.listdir(os.getcwd()) if f.startswith("mantenimiento_") and f.endswith(".txt")], reverse=True)
        last_date = "Nunca"
        if last_log:
            try:
                last_date = last_log[0].replace("mantenimiento_", "").replace(".txt", "")
            except:
                pass

        warning_label = tk.Label(
            confirm_win,
            text=f"⚠️ No realices mantenimiento seguido.\nRecomendado: 1 vez por semana.\nÚltimo mantenimiento: {last_date}",
            fg=COLOR_ACCENT,
            bg=COLOR_BG,
            font=(MODERN_FONT, 11, "bold"),
            justify="center",
            wraplength=350
        )
        warning_label.pack(pady=20)

        btn_frame = tk.Frame(confirm_win, bg=COLOR_BG)
        btn_frame.pack(pady=10)

        def start_maintenance():
            self._maintenance_confirmed = True
            confirm_win.destroy()
            threading.Thread(target=self._run_maintenance_thread, daemon=True).start()

        accept_btn = tk.Button(
            btn_frame,
            text="Aceptar",
            font=(MODERN_FONT, 10, "bold"),
            bg=COLOR_HOVER,
            fg="#FFFFFF",
            command=start_maintenance,
            relief="flat"
        )
        accept_btn.pack(side="left", padx=10)

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancelar",
            font=(MODERN_FONT, 10),
            bg=COLOR_WARNING,
            fg="#FFFFFF",
            command=confirm_win.destroy,
            relief="flat"
        )
        cancel_btn.pack(side="right", padx=10)
    
    def show_error(self, message):
        """Muestra un mensaje de error"""
        messagebox.showerror("Error", message)
    
    def create_license_button(self, parent):
        """Crea el botón para ver información de la licencia"""
        license_btn = tk.Button(parent, text="🔍 Ver Licencia", 
                              command=self.show_license_info,
                              bg="#330066", fg="#FFFFFF", 
                              font=(MODERN_FONT, 8, "bold"),
                              relief="flat", padx=10, pady=5,
                              cursor="hand2")
        license_btn.place(relx=0.98, rely=0.98, anchor="se")
        
        def on_enter(e):
            license_btn.config(bg=COLOR_HOVER)
        
        def on_leave(e):
            license_btn.config(bg="#330066")
        
        license_btn.bind("<Enter>", on_enter)
        license_btn.bind("<Leave>", on_leave)

    def show_license_info(self):
        """Muestra la información de la licencia actual"""
        # Implementación simplificada para el refactor, reutilizando lógica existente si posible
        # o delegando a un módulo de licencia/UI si extrajéramos eso también.
        # Por ahora lo mantenemos aquí o podríamos moverlo a ui/dialogs.py también.
        # Para simplificar, lo dejaré aquí pero usando las utilidades.
        
        username, expiry_date = self.get_current_license_info()
        
        info_window = tk.Toplevel(self.root)
        info_window.title("Información de Licencia")
        info_window.geometry("400x250")
        info_window.configure(bg=COLOR_BG)
        info_window.resizable(False, False)
        info_window.transient(self.root)
        info_window.grab_set()
        
        info_window.update_idletasks()
        x = (info_window.winfo_screenwidth() // 2) - (200)
        y = (info_window.winfo_screenheight() // 2) - (125)
        info_window.geometry(f"400x250+{x}+{y}")
        
        main_frame = tk.Frame(info_window, bg=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = tk.Label(main_frame, text="📄 INFORMACIÓN DE LICENCIA", 
                              font=(MODERN_FONT, 14, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG)
        title_label.pack(pady=(0, 20))
        
        user_frame = tk.Frame(main_frame, bg=COLOR_BG)
        user_frame.pack(fill="x", pady=10)
        
        tk.Label(user_frame, text="Usuario:", 
                font=(MODERN_FONT, 11, "bold"), fg="#FFFFFF", bg=COLOR_BG).pack(anchor="w")
        
        user_value = tk.Label(user_frame, text=username if username else "No registrado", 
                             font=(MODERN_FONT, 11), fg=COLOR_TEXT, bg=COLOR_BG)
        user_value.pack(anchor="w", pady=(5, 0))
        
        expiry_frame = tk.Frame(main_frame, bg=COLOR_BG)
        expiry_frame.pack(fill="x", pady=10)
        
        tk.Label(expiry_frame, text="Fecha de expiración:", 
                font=(MODERN_FONT, 11, "bold"), fg="#FFFFFF", bg=COLOR_BG).pack(anchor="w")
        
        # Helper interno para validar fecha
        def is_license_valid(expiry_date_str):
            try:
                day, month, year = map(int, expiry_date_str.split('/'))
                expiry_date = datetime.datetime(year, month, day)
                return expiry_date > datetime.datetime.now()
            except:
                return False

        # Note: necesitamos datetime aqui
        import datetime
        
        is_valid = False
        if expiry_date:
            try:
                 day, month, year = map(int, expiry_date.split('/'))
                 if datetime.datetime(year, month, day) > datetime.datetime.now():
                     is_valid = True
            except:
                pass

        expiry_value = tk.Label(expiry_frame, text=expiry_date if expiry_date else "Sin licencia activa", 
                               font=(MODERN_FONT, 11), 
                               fg=COLOR_TEXT if is_valid else COLOR_WARNING, 
                               bg=COLOR_BG)
        expiry_value.pack(anchor="w", pady=(5, 0))
        
        status_frame = tk.Frame(main_frame, bg=COLOR_BG)
        status_frame.pack(fill="x", pady=10)
        
        tk.Label(status_frame, text="Estado:", 
                font=(MODERN_FONT, 11, "bold"), fg="#FFFFFF", bg=COLOR_BG).pack(anchor="w")
        
        status_text = "VENCIDA"
        status_color = COLOR_WARNING
        
        if not username or not expiry_date:
            status_text = "SIN LICENCIA"
        elif is_valid:
            status_text = "ACTIVA"
            status_color = COLOR_TEXT
            
        status_value = tk.Label(status_frame, text=status_text, 
                               font=(MODERN_FONT, 11, "bold"), fg=status_color, bg=COLOR_BG)
        status_value.pack(anchor="w", pady=(5, 0))
        
        close_btn = tk.Button(main_frame, text="Cerrar", 
                             command=info_window.destroy,
                             bg=COLOR_HOVER, fg="#FFFFFF", 
                             font=(MODERN_FONT, 10, "bold"),
                             relief="flat", padx=20, pady=5)
        close_btn.pack(pady=(20, 0))

    def get_current_license_info(self):
        """Obtiene la información de la licencia actual desde un archivo de configuración"""
        config_path = os.path.join(os.path.dirname(sys.argv[0]), "cache_core_license.cfg")
        
        username = None
        expiry_date = None
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    username = data.get('username', '')
                    expiry_timestamp = data.get('expiry_date', 0)
                    
                    if expiry_timestamp:
                        import datetime
                        expiry_date = datetime.datetime.fromtimestamp(expiry_timestamp).strftime('%d/%m/%Y')
        except:
            pass
        
        return username, expiry_date
    
    def load_background_image(self):
        """Carga la imagen de fondo estática desde la carpeta assets"""
        try:
            # Rutas posibles para la imagen de fondo
            bg_paths = [
                os.path.join(os.path.dirname(__file__), "assets", "background.png"),
                os.path.join(os.path.dirname(__file__), "assets", "background.jpg"),
                os.path.join(os.getcwd(), "assets", "background.png"),
                os.path.join(os.getcwd(), "assets", "background.jpg")
            ]
            
            for path in bg_paths:
                if os.path.exists(path):
                    img = Image.open(path)
                    # Redimensionar a 16:9 - 1280x720
                    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                    self.bg_photo = ImageTk.PhotoImage(img)
                    self.bg_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
                    return
            
            # Si no se encuentra imagen, usar color de fondo simple
            self.bg_canvas.create_rectangle(0, 0, 1280, 720, fill=COLOR_BG, outline="")
            
        except Exception as e:
            print(f"Error cargando imagen de fondo: {e}")
            # Fondo de respaldo
            self.bg_canvas.create_rectangle(0, 0, 1280, 720, fill=COLOR_BG, outline="")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        if messagebox.askokcancel("Salir", "¿Estás seguro de que quieres salir de Windows-Optimizer-V1?"):
            def fade_out(alpha=1.0):
                if alpha > 0.0:
                    self.root.attributes('-alpha', alpha)
                    self.root.after(10, fade_out, alpha - 0.05)
                else:
                    self.root.destroy()
            
            fade_out()

if __name__ == "__main__":
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass
        
    app = CacheCoreApp()
    app.root.mainloop()
