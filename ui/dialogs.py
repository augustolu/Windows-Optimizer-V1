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
    """Dialogo de contrasena moderno"""
    def __init__(self, password_hash):
        self.password_hash = password_hash
        self.result = False
        
        self.dialog = tk.Tk()
        self.dialog.title("CACHE_CORE x64 - Acceso Seguro")
        self.dialog.geometry("450x450")
        self.dialog.configure(bg="#0a0015")
        self.dialog.resizable(False, False)
        
        self.center_dialog()
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.create_widgets()
        
    def center_dialog(self):
        """Centra el dialogo en la pantalla"""
        self.dialog.update_idletasks()
        width = 450
        height = 450
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f"{width}x{height}+{x}+{y}")
    
    def create_widgets(self):
        """Crea los widgets del dialogo de contrasena"""
        main_frame = Frame(self.dialog, bg="#0a0015")
        main_frame.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Logo
        self.create_logo(main_frame)
        
        # Titulo
        title_label = Label(main_frame, text="ACCESO SEGURO", 
                          font=(MODERN_FONT, 20, "bold"), fg="#e1bee7", bg="#0a0015")
        title_label.pack(pady=(10, 5))
        
        subtitle_label = Label(main_frame, text="Sistema de Optimizacion Profesional", 
                             font=(MODERN_FONT, 10), fg="#9575cd", bg="#0a0015")
        subtitle_label.pack(pady=(0, 30))
        
        # Frame de contrasena
        password_frame = Frame(main_frame, bg="#0a0015")
        password_frame.pack(pady=10)
        
        Label(password_frame, text="Contrasena:", 
             font=(MODERN_FONT, 11), fg="#FFFFFF", bg="#0a0015").pack()
        
        self.password_var = tk.StringVar()
        password_entry = Entry(password_frame, textvariable=self.password_var, 
                              show="*", font=(MODERN_FONT, 12), width=25, 
                              bg="#2D004D", fg="#FFFFFF", relief="solid",
                              insertbackground="#FFFFFF", bd=1)
        password_entry.pack(pady=10, ipady=8)
        password_entry.focus_set()
        
        # Botones
        button_frame = Frame(main_frame, bg="#0a0015")
        button_frame.pack(pady=20)
        
        Button(button_frame, text="ACCEDER", command=self.validate_password,
              bg="#6200ea", fg="#FFFFFF", font=(MODERN_FONT, 10, "bold"),
              relief="flat", padx=20, pady=8, cursor="hand2").pack(side="left", padx=10)
        
        Button(button_frame, text="CANCELAR", command=self.on_closing,
              bg="#c62828", fg="#FFFFFF", font=(MODERN_FONT, 10, "bold"),
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
                
                logo_label = Label(parent, image=logo_img, bg="#0a0015")
                logo_label.image = logo_img
                logo_label.pack(pady=10)
                return
            
        except:
            pass
        
        logo_canvas = tk.Canvas(parent, width=80, height=80, bg="#0a0015", highlightthickness=0)
        logo_canvas.pack(pady=10)
        logo_canvas.create_oval(10, 10, 70, 70, fill="#6200ea", outline="")
        logo_canvas.create_text(40, 40, text="CC", fill="#FFFFFF", font=(MODERN_FONT, 20, "bold"))
    
    def validate_password(self):
        """Valida la contrasena ingresada"""
        password = self.password_var.get()
        if not password:
            self.shake_dialog()
            return

        if hashlib.sha256(password.encode()).hexdigest() == self.password_hash:
            self.result = True
            self.save_license_info("Usuario General", None)
            self.dialog.quit()
            self.dialog.destroy()
            return

        hardware_id = HardwareIDGenerator.get_hardware_id()
        is_valid, message, username, expiry_date = LicenseValidator.validate_password(password, hardware_id)
        if is_valid:
            self.result = True
            self.save_license_info(username, expiry_date)
            self.dialog.quit()
            self.dialog.destroy()
        else:
            if message == "CLAVE VENCIDA":
                messagebox.showerror("Licencia Vencida", "Su licencia ha expirado. Por favor contacte al soporte.")
            else:
                messagebox.showerror("Acceso Denegado", "Contrasena o licencia invalida.")
            self.shake_dialog()
            self.password_var.set("")
    
    def save_license_info(self, username, expiry_date):
        """Guarda la informacion de la licencia en un archivo de configuracion"""
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
            print(f"Error guardando informacion de licencia: {e}")
    
    def shake_dialog(self):
        """Animacion de sacudida para error de contrasena"""
        x = self.dialog.winfo_x()
        y = self.dialog.winfo_y()
        
        for offset in [10, -10, 8, -8, 5, -5, 0]:
            self.dialog.geometry(f"+{x + offset}+{y}")
            self.dialog.update()
            time.sleep(0.02)
    
    def on_closing(self):
        """Maneja el cierre del dialogo"""
        self.dialog.quit()
        self.dialog.destroy()
