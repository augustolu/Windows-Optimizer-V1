import os
import sys
import json
import hashlib

# Configuración - Contraseña universal: 10020302
CONFIG_FILE = "cache_core_config.cfg"
PASSWORD = "10020302"
PASSWORD_HASH = hashlib.sha256(PASSWORD.encode()).hexdigest()

# Secreto para la generación y validación de licencias
SECRET = b'cache_core_secret_2025'

# Configuración de archivos
RESOURCES_7Z = "post_install.7z"
RESOURCES_FOLDER = "post_install"
LOGO_FILE = "logocache.png"
ANYDESK_EXE = "anydesk.exe"

# Fuente moderna
MODERN_FONT = "Roboto"
FALLBACK_FONT = "Arial"

# Colores de la aplicación
COLOR_BG = "#1E0033"
COLOR_ACCENT = "#CC00FF"
COLOR_TEXT = "#00FF88"
COLOR_WARNING = "#FF0066"
COLOR_HOVER = "#4C007D"

MULTI_LINE_FONT = "Consolas"

def load_config():
    """Carga la configuración desde archivo"""
    config_path = os.path.join(os.path.dirname(sys.argv[0]), CONFIG_FILE)
    default_config = {
        'no_lazy_mode': False,
        'win_priority_control': False
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error al cargar configuración: {e}")
    return default_config

def save_config(config):
    """Guarda la configuración en archivo"""
    try:
        config_path = os.path.join(os.path.dirname(sys.argv[0]), CONFIG_FILE)
        with open(config_path, 'w') as f:
            json.dump(config, f)
        return True
    except Exception as e:
        print(f"Error al guardar configuración: {e}")
        return False
