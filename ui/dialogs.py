import tkinter as tk
from tkinter import Frame, Label, Entry, Button, messagebox
import os
import sys
import time
import json
import hashlib
from datetime import datetime
from PIL import Image, ImageTk

from config.settings import (
    COLOR_BG, COLOR_ACCENT, COLOR_HOVER, COLOR_WARNING, COLOR_TEXT,
    MODERN_FONT, LOGO_FILE, RESOURCES_FOLDER
)
from features.security import LicenseValidator, HardwareIDGenerator

class ModernPasswordDialog:
    """Diálogo de contraseña moderno con animaciones"""
    def __init__(self, password_hash):
        self.password_hash = password_hash
        self.result = False
        
        self.dialog = tk.Tk()
        self.dialog.title("CACHE_CORE x64 - Acceso Seguro")
        self.dialog.geometry("500x350")
        self.dialog.configure(bg=COLOR_BG)
        self.dialog.resizable(False, False)
        self.dialog.withdraw()
        
        self.center_dialog()
        
        self.dialog.focus_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
        self.animate_entrance()
        
    def center_dialog(self):
        """Centra el diálogo en la pantalla"""
        self.dialog.update_idletasks()
        width = 500
        height = 350
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Crea los widgets del diálogo de contraseña"""
        main_frame = Frame(self.dialog, bg=COLOR_BG)
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        self.create_logo(main_frame)
        
        title_label = Label(main_frame, text="🔒 ACCESO SEGURO", 
                          font=(MODERN_FONT, 20, "bold"), fg=COLOR_ACCENT, bg=COLOR_BG)
        title_label.pack(pady=(20, 5))
        
        subtitle_label = Label(main_frame, text="Sistema de Optimización Profesional", 
                             font=(MODERN_FONT, 12), fg="#9900CC", bg=COLOR_BG)
        subtitle_label.pack(pady=(0, 20))
        
        password_frame = Frame(main_frame, bg=COLOR_BG)
        password_frame.pack(pady=10)
        
        Label(password_frame, text="Contraseña:", 
             font=(MODERN_FONT, 11), fg="#FFFFFF", bg=COLOR_BG).pack()
        
        self.password_var = tk.StringVar()
        password_entry = Entry(password_frame, textvariable=self.password_var, 
                              show="•", font=(MODERN_FONT, 12), width=25, 
                              bg="#2D004D", fg="#FFFFFF", relief="flat",
                              insertbackground="#FFFFFF")
        password_entry.pack(pady=10, ipady=8)
        password_entry.focus()
        
        button_frame = Frame(main_frame, bg=COLOR_BG)
        button_frame.pack(pady=20)
        
        Button(button_frame, text="🔓 ACCEDER", command=self.validate_password,
              bg=COLOR_HOVER, fg="#FFFFFF", font=(MODERN_FONT, 10, "bold"),
              relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=10)
        
        Button(button_frame, text="✖ CANCELAR", command=self.on_closing,
              bg=COLOR_WARNING, fg="#FFFFFF", font=(MODERN_FONT, 10, "bold"),
              relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=10)
        
        password_entry.bind('<Return>', lambda event: self.validate_password())
    
    def create_logo(self, parent):
        """Crea el logo"""
        try:
            logo_paths = [
                LOGO_FILE,
                os.path.join(os.path.dirname(__file__), "..", LOGO_FILE),
                os.path.join(os.getcwd(), LOGO_FILE),
                os.path.join(os.path.dirname(sys.argv[0]), LOGO_FILE)
            ]
            
            logo_path = None
            for path in logo_paths:
                if os.path.exists(path):
                    logo_path = path
                    break
            
            if logo_path:
                img = Image.open(logo_path)
                img = img.resize((80, 80), Image.Resampling.LANCZOS)
                logo_img = ImageTk.PhotoImage(img)
                
                logo_label = Label(parent, image=logo_img, bg=COLOR_BG)
                logo_label.image = logo_img
                logo_label.pack(pady=10)
                return
            
        except:
            pass
        
        logo_canvas = tk.Canvas(parent, width=80, height=80, bg=COLOR_BG, highlightthickness=0)
        logo_canvas.pack(pady=10)
        logo_canvas.create_oval(10, 10, 70, 70, fill=COLOR_HOVER, outline="")
        logo_canvas.create_text(40, 40, text="CC", fill="#FFFFFF", font=(MODERN_FONT, 20, "bold"))
    
    def animate_entrance(self):
        """Animación de entrada para el diálogo"""
        self.dialog.attributes('-alpha', 0.0)
        self.dialog.deiconify()
        
        def fade_in(alpha=0.0):
            if alpha < 1.0:
                self.dialog.attributes('-alpha', alpha)
                self.dialog.after(10, fade_in, alpha + 0.05)
            else:
                self.dialog.attributes('-alpha', 1.0)
        
        fade_in()
    
    def validate_password(self):
        """Valida la contraseña ingresada"""
        password = self.password_var.get()
        if not password:
            self.shake_dialog()
            return

        # Check if general password
        if hashlib.sha256(password.encode()).hexdigest() == self.password_hash:
            self.result = True
            self.save_license_info("Usuario General", None)
            self.animate_exit()
            return

        # Check if license key
        hardware_id = HardwareIDGenerator.get_hardware_id()
        is_valid, message, username, expiry_date = LicenseValidator.validate_password(password, hardware_id)
        if is_valid:
            self.result = True
            self.save_license_info(username, expiry_date)
            self.animate_exit()
        else:
            if message == "CLAVE VENCIDA":
                messagebox.showerror("Licencia Vencida", "Su licencia ha expirado. Por favor contacte al soporte.")
            else:
                messagebox.showerror("Acceso Denegado", "Contraseña o licencia inválida.")
            self.shake_dialog()
            self.password_var.set("")
    
    def save_license_info(self, username, expiry_date):
        """Guarda la información de la licencia en un archivo de configuración"""
        try:
            config_path = os.path.join(os.path.dirname(sys.argv[0]), "cache_core_license.cfg")
            
            expiry_timestamp = 0
            if expiry_date:
                expiry_timestamp = datetime.strptime(expiry_date, "%Y%m%d").timestamp()
            
            data = {
                'username': username,
                'expiry_date': expiry_timestamp,
                'activation_date': datetime.now().timestamp()
            }
            
            with open(config_path, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error guardando información de licencia: {e}")
    
    def animate_exit(self):
        """Animación de salida para el diálogo"""
        def fade_out(alpha=1.0):
            if alpha > 0.0:
                self.dialog.attributes('-alpha', alpha)
                self.dialog.after(10, fade_out, alpha - 0.05)
            else:
                self.dialog.quit()
                self.dialog.destroy()
        
        fade_out()
    
    def shake_dialog(self):
        """Animación de sacudida para error de contraseña"""
        x = self.dialog.winfo_x()
        y = self.dialog.winfo_y()
        
        for offset in [10, -10, 8, -8, 5, -5, 0]:
            self.dialog.geometry(f"+{x + offset}+{y}")
            self.dialog.update()
            time.sleep(0.02)
    
    def on_closing(self):
        """Maneja el cierre del diálogo"""
        self.animate_exit()
