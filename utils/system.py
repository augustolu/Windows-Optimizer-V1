import subprocess
import sys
import ctypes

def is_admin():
    """Verifica permisos de administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_command_in_shell(command, timeout=30):
    """Ejecuta un comando en shell y devuelve si fue exitoso (True/False)"""
    try:
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
        
        result = subprocess.run(command, shell=True, capture_output=True, 
                              text=True, timeout=timeout, startupinfo=startupinfo)
        
        return result.returncode == 0
    except Exception:
        return False
