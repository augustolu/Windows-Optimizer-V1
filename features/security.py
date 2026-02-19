import wmi
import hashlib
import uuid
import hmac
import json
import os
import sys
from datetime import datetime
from config.settings import SECRET, PASSWORD_HASH

class HardwareIDGenerator:
    """Generador de ID único basado en hardware"""
    @staticmethod
    def get_hardware_id():
        """Obtiene un ID único basado en componentes del hardware"""
        try:
            c = wmi.WMI()
            system_info = ""
            
            for board in c.Win32_BaseBoard():
                system_info += board.Manufacturer + board.Product + board.SerialNumber
            
            for cpu in c.Win32_Processor():
                system_info += cpu.ProcessorId
            
            for disk in c.Win32_DiskDrive():
                if disk.SerialNumber:
                    system_info += disk.SerialNumber
                    break
            
            for bios in c.Win32_BIOS():
                system_info += bios.SerialNumber
            
            if not system_info:
                system_info = str(uuid.getnode())
            
            hardware_hash = hashlib.sha256(system_info.encode()).hexdigest()
            return hardware_hash[:16].upper()
        except Exception:
            return hashlib.sha256(str(uuid.getnode()).encode()).hexdigest()[:16].upper()

class LicenseValidator:
    """Validador de licencias para el programa principal"""
    @staticmethod
    def validate_password(password, hardware_id):
        """Valida una contraseña de licencia y devuelve información adicional"""
        clean_password = password.replace("-", "").lower()
        if len(clean_password) != 32:
            return False, "Contraseña inválida", None, None
        
        date_str = clean_password[:8]
        sig_part = clean_password[8:]
        
        try:
            exp_date = datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            return False, "Contraseña inválida", None, None
        
        if exp_date < datetime.now():
            return False, "CLAVE VENCIDA", None, date_str
        
        data = exp_date.strftime("%Y-%m-%d") + "|" + hardware_id
        expected_sig = hmac.new(SECRET, data.encode(), hashlib.sha256).hexdigest()[:24].lower()
        
        if sig_part != expected_sig:
            return False, "Contraseña inválida", None, None
        
        username = f"Usuario_{hardware_id[:6]}"
        try:
            config_path = os.path.join(os.path.dirname(sys.argv[0]), "cache_core_license.cfg")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    username = data.get('username', username)
        except Exception:
            pass
        
        return True, "Licencia válida", username, date_str
