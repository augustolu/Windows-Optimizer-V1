import customtkinter as ctk
from tkinter import messagebox, simpledialog
import threading
import sys
import os
import base64
import time
from PIL import Image

# Imports de nuestros módulos
from config.settings import (
    COLOR_BG, COLOR_ACCENT, COLOR_TEXT, COLOR_WARNING, COLOR_HOVER,
    MODERN_FONT, LOGO_FILE, RESOURCES_FOLDER, PASSWORD_HASH,
    load_config, save_config
)
from utils.system import is_admin, run_command_in_shell
from utils.files import extract_7z_resources, run_anydesk
from utils.registry import set_registry_value
from ui.dialogs import ModernPasswordDialog
from features.security import HardwareIDGenerator
from features.optimization import SystemOptimizer
from features.maintenance import SystemMaintenance

# Configurar CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class WindowsOptimizerApp:
    def __init__(self):
        # Verificar permisos de administrador primero
        if not is_admin():
            messagebox.showerror("Error", "ERROR: Se necesitan permisos de administrador.")
            sys.exit(1)
            
        # Ejecutar AnyDesk antes de pedir la contraseña
        run_anydesk()
            
        # Verificar contraseña universal o licencia
        if not self.check_password():
            sys.exit(1)
            
        # Crear ventana principal después de la autenticación
        self.root = ctk.CTk()
        self.setup_window()
        self.create_widgets()
        
        # Inicializar logs
        self.add_log("✅ Sistema Windows-Optimizer-V1 iniciado correctamente")
        self.add_log("💫 Sistema de Optimización Avanzado para Windows")
        self.add_log("=" * 50)
        
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
        self.root.title("Windows-Optimizer-V1 - Sistema de Optimización Avanzado")
        
        # Aspect ratio 16:9 - 1280x720
        width = 1280
        height = 720
        
        # Centrar ventana
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.resizable(False, False)
        
        # Color de fondo - transparente para mostrar imagen de fondo
        self.root.configure(fg_color="transparent")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        # Cargar imagen de fondo
        self.load_background_image()
        
        # Frame principal con efecto de transparencia - ahora totalmente transparente
        self.main_frame = ctk.CTkFrame(
            self.root,
            width=1200,
            height=660,
            fg_color="transparent",  # Transparente para ver el fondo
            corner_radius=0,
            border_width=0
        )
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Contenido del frame principal
        self.create_header()
        self.create_main_buttons()
        self.create_console()
        self.create_footer()
        self.create_license_button()
    
    def load_background_image(self):
        """Carga la imagen de fondo estática desde la carpeta assets"""
        try:
            bg_paths = [
                os.path.join(os.path.dirname(__file__), "assets", "background.png"),
                os.path.join(os.path.dirname(__file__), "assets", "background.jpg"),
                os.path.join(os.getcwd(), "assets", "background.png"),
                os.path.join(os.getcwd(), "assets", "background.jpg")
            ]
            
            for path in bg_paths:
                if os.path.exists(path):
                    # Cargar y mostrar imagen
                    bg_image = Image.open(path)
                    bg_image = bg_image.resize((1280, 720), Image.Resampling.LANCZOS)
                    
                    self.bg_image_ctk = ctk.CTkImage(
                        light_image=bg_image,
                        dark_image=bg_image,
                        size=(1280, 720)
                    )
                    
                    self.bg_label = ctk.CTkLabel(
                        self.root,
                        image=self.bg_image_ctk,
                        text=""
                    )
                    self.bg_label.place(x=0, y=0)
                    return
        except Exception as e:
            print(f"Error cargando imagen de fondo: {e}")
    
    def create_header(self):
        """Crea el encabezado con logo y título"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(pady=(20, 10))
        
        # Logo
        self.load_logo(header_frame)
        
        # Título
        title_label = ctk.CTkLabel(
            header_frame,
            text="Windows-Optimizer-V1",
            font=(MODERN_FONT, 32, "bold"),
            text_color=COLOR_ACCENT
        )
        title_label.pack(pady=(10, 0))
        
        # Subtítulo
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Sistema de Optimización Avanzado",
            font=(MODERN_FONT, 14),
            text_color="#9900CC"
        )
        subtitle_label.pack()
    
    def load_logo(self, parent):
        """Carga el logo desde archivo"""
        try:
            logo_paths = [
                LOGO_FILE,
                os.path.join(os.path.dirname(__file__), LOGO_FILE),
                os.path.join(os.getcwd(), LOGO_FILE),
            ]
            
            for path in logo_paths:
                if os.path.exists(path):
                    logo_image = Image.open(path)
                    logo_image = logo_image.resize((80, 80), Image.Resampling.LANCZOS)
                    
                    logo_ctk = ctk.CTkImage(
                        light_image=logo_image,
                        dark_image=logo_image,
                        size=(80, 80)
                    )
                    
                    logo_label = ctk.CTkLabel(parent, image=logo_ctk, text="")
                    logo_label.image = logo_ctk
                    logo_label.pack()
                    return True
        except Exception as e:
            print(f"Error cargando logo: {e}")
        
        return False
    
    def create_main_buttons(self):
        """Crea los botones principales"""
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=15)
        
        # Botón Optimización
        self.optimize_btn = ctk.CTkButton(
            button_frame,
            text="⚡ OPTIMIZACIÓN DEL SISTEMA",
            width=350,
            height=55,
            font=(MODERN_FONT, 14, "bold"),
            fg_color=COLOR_HOVER,
            hover_color="#6A00CC",
            corner_radius=10,
            command=self.run_optimization
        )
        self.optimize_btn.pack(pady=8)
        
        # Botón Mantenimiento
        self.maintenance_btn = ctk.CTkButton(
            button_frame,
            text="🔧 MANTENIMIENTO AVANZADO",
            width=350,
            height=55,
            font=(MODERN_FONT, 14, "bold"),
            fg_color=COLOR_HOVER,
            hover_color="#6A00CC",
            corner_radius=10,
            command=self.run_maintenance
        )
        self.maintenance_btn.pack(pady=8)
        
        # Frame para botones toggle
        config_frame = ctk.CTkFrame(button_frame, fg_color="transparent")
        config_frame.pack(pady=10)
        
        config = load_config()
        
        # Botón NoLazyMode
        self.no_lazy_btn = ctk.CTkButton(
            config_frame,
            text="⚡ ACTIVAR NoLazyMode" if not config['no_lazy_mode'] else "🛑 DESACTIVAR NoLazyMode",
            width=240,
            height=45,
            font=(MODERN_FONT, 12, "bold"),
            fg_color="#4C007D" if not config['no_lazy_mode'] else COLOR_WARNING,
            hover_color="#6A00CC" if not config['no_lazy_mode'] else "#FF3388",
            corner_radius=8,
            command=self.toggle_no_lazy_mode
        )
        self.no_lazy_btn.pack(side="left", padx=5)
        
        # Botón WinPriority
        self.win_priority_btn = ctk.CTkButton(
            config_frame,
            text="⚡ ACTIVAR WinPriority" if not config['win_priority_control'] else "🛑 DESACTIVAR WinPriority",
            width=240,
            height=45,
            font=(MODERN_FONT, 12, "bold"),
            fg_color="#4C007D" if not config['win_priority_control'] else COLOR_WARNING,
            hover_color="#6A00CC" if not config['win_priority_control'] else "#FF3388",
            corner_radius=8,
            command=self.toggle_win_priority_control
        )
        self.win_priority_btn.pack(side="left", padx=5)
        
        # Botón Generar Licencia
        self.generate_key_btn = ctk.CTkButton(
            button_frame,
            text="🔑 GENERAR CLAVE DE LICENCIA",
            width=350,
            height=55,
            font=(MODERN_FONT, 14, "bold"),
            fg_color=COLOR_HOVER,
            hover_color="#6A00CC",
            corner_radius=10,
            command=self.generate_request_code
        )
        self.generate_key_btn.pack(pady=8)
    
    def create_console(self):
        """Crea la consola de logs"""
        console_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        console_frame.pack(fill="both", expand=True, pady=10, padx=20)
        
        self.console_text = ctk.CTkTextbox(
            console_frame,
            height=180,
            font=("Consolas", 11),
            fg_color="#0A0015",
            text_color=COLOR_TEXT,
            corner_radius=8,
            border_width=1,
            border_color="#9900CC"
        )
        self.console_text.pack(fill="both", expand=True)
        self.console_text.configure(state="disabled")
    
    def add_log(self, message):
        """Añade un mensaje al log"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.console_text.configure(state="normal")
        self.console_text.insert("end", formatted_message + "\n")
        self.console_text.see("end")
        self.console_text.configure(state="disabled")
    
    def create_footer(self):
        """Crea el footer con derechos reservados"""
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.pack(pady=8)
        
        copyright_text = "© 2025 Windows-Optimizer-V1 - Todos los derechos reservados"
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text=copyright_text,
            font=(MODERN_FONT, 10),
            text_color="#9900CC"
        )
        copyright_label.pack()
        
        warning_text = "Sistema protegido - Distribución no autorizada prohibida"
        warning_label = ctk.CTkLabel(
            footer_frame,
            text=warning_text,
            font=(MODERN_FONT, 9, "italic"),
            text_color=COLOR_WARNING
        )
        warning_label.pack()
    
    def create_license_button(self):
        """Crea el botón para ver información de la licencia"""
        license_btn = ctk.CTkButton(
            self.main_frame,
            text="🔍 Ver Licencia",
            width=100,
            height=28,
            font=(MODERN_FONT, 9, "bold"),
            fg_color="#330066",
            hover_color=COLOR_HOVER,
            corner_radius=5,
            command=self.show_license_info
        )
        license_btn.place(relx=0.98, rely=0.98, anchor="se")
    
    def toggle_no_lazy_mode(self):
        """Activa/desactiva el modo NoLazyMode"""
        config = load_config()
        new_state = not config['no_lazy_mode']
        
        if new_state:
            cmd = 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NoLazyMode" /t REG_DWORD /d "1" /f'
            success = run_command_in_shell(cmd)
            if success:
                self.add_log("✅ NoLazyMode ACTIVADO")
                config['no_lazy_mode'] = True
            else:
                self.add_log("❌ Error al activar NoLazyMode")
                return
        else:
            cmd = 'reg delete "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NoLazyMode" /f'
            success = run_command_in_shell(cmd)
            if success:
                self.add_log("✅ NoLazyMode DESACTIVADO")
                config['no_lazy_mode'] = False
            else:
                self.add_log("❌ Error al desactivar NoLazyMode")
                return
        
        if save_config(config):
            self.update_toggle_buttons()
        else:
            self.add_log("❌ Error al guardar configuración")
    
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
                self.add_log("✅ Win32PrioritySeparation ACTIVADO (0x2A)")
                config['win_priority_control'] = True
            else:
                self.add_log("❌ Error al activar Win32PrioritySeparation")
                return
        else:
            success = set_registry_value(
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\PriorityControl",
                "Win32PrioritySeparation", 0x28
            )
            if success:
                self.add_log("✅ Win32PrioritySeparation DESACTIVADO (0x28)")
                config['win_priority_control'] = False
            else:
                self.add_log("❌ Error al desactivar Win32PrioritySeparation")
                return
        
        if save_config(config):
            self.update_toggle_buttons()
        else:
            self.add_log("❌ Error al guardar configuración")
    
    def update_toggle_buttons(self):
        """Actualiza el estado visual de los botones toggle"""
        config = load_config()
        
        # Actualizar NoLazyMode
        if config['no_lazy_mode']:
            self.no_lazy_btn.configure(
                text="🛑 DESACTIVAR NoLazyMode",
                fg_color=COLOR_WARNING,
                hover_color="#FF3388"
            )
        else:
            self.no_lazy_btn.configure(
                text="⚡ ACTIVAR NoLazyMode",
                fg_color="#4C007D",
                hover_color="#6A00CC"
            )
        
        # Actualizar WinPriority
        if config['win_priority_control']:
            self.win_priority_btn.configure(
                text="🛑 DESACTIVAR WinPriority",
                fg_color=COLOR_WARNING,
                hover_color="#FF3388"
            )
        else:
            self.win_priority_btn.configure(
                text="⚡ ACTIVAR WinPriority",
                fg_color="#4C007D",
                hover_color="#6A00CC"
            )
    
    def run_optimization(self):
        """Ejecuta la optimización del sistema"""
        threading.Thread(target=self._run_optimization_thread, daemon=True).start()
    
    def _run_optimization_thread(self):
        self.optimize_btn.configure(state="disabled")
        
        SystemOptimizer.run_optimization(self.add_log)
        
        self.add_log("🧹 Limpiando logs en 3 segundos...")
        time.sleep(3)
        self.console_text.configure(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.configure(state="disabled")
        self.add_log("✅ Optimización completada - Sistema listo")
        
        self.optimize_btn.configure(state="normal")
    
    def run_maintenance(self):
        """Ejecuta el mantenimiento del sistema"""
        self.confirm_maintenance()
    
    def _run_maintenance_thread(self):
        if not hasattr(self, '_maintenance_confirmed') or not self._maintenance_confirmed:
            return
        
        self._maintenance_confirmed = False
        self.maintenance_btn.configure(state="disabled")
        
        SystemMaintenance.run_maintenance(self.add_log)
        
        self.maintenance_btn.configure(state="normal")
    
    def confirm_maintenance(self):
        """Muestra una ventana de confirmación para el mantenimiento"""
        response = messagebox.askyesno(
            "Confirmación de Mantenimiento",
            "⚠️ No realices mantenimiento seguido.\nRecomendado: 1 vez por semana.\n\n¿Deseas continuar?"
        )
        
        if response:
            self._maintenance_confirmed = True
            threading.Thread(target=self._run_maintenance_thread, daemon=True).start()
    
    def generate_request_code(self):
        """Genera el código de solicitud para la licencia"""
        username = simpledialog.askstring("Nombre de Usuario", "Ingrese el nombre de usuario:")
        if not username:
            return
        
        hardware_id = HardwareIDGenerator.get_hardware_id()
        data = username + "|" + hardware_id
        request_code = base64.b64encode(data.encode()).decode()
        
        messagebox.showinfo(
            "Código de Solicitud",
            f"Código generado:\n\n{request_code}\n\nCopia este código para solicitar tu licencia."
        )
    
    def show_license_info(self):
        """Muestra la información de la licencia actual"""
        messagebox.showinfo(
            "Información de Licencia",
            "Funcionalidad de licencia disponible.\nUsa 'Generar Clave de Licencia' para obtener tu código."
        )
    
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
        
    app = WindowsOptimizerApp()
    app.root.mainloop()
