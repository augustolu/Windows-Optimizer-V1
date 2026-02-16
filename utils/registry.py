import winreg

def ensure_registry_key(key_path):
    """Asegura que la clave de registro exista, creándola si es necesario"""
    try:
        if "HKEY_LOCAL_MACHINE" in key_path:
            base_key = winreg.HKEY_LOCAL_MACHINE
            sub_key = key_path.replace("HKEY_LOCAL_MACHINE\\", "")
        elif "HKEY_CURRENT_USER" in key_path:
            base_key = winreg.HKEY_CURRENT_USER
            sub_key = key_path.replace("HKEY_CURRENT_USER\\", "")
        else:
            return False
        winreg.CreateKeyEx(base_key, sub_key, 0, winreg.KEY_SET_VALUE)
        return True
    except Exception as e:
        print(f"Error al crear clave de registro: {e}")
        return False

def set_registry_value(key_path, value_name, value_data, value_type=winreg.REG_DWORD):
    """Establece un valor en el registro de Windows"""
    try:
        ensure_registry_key(key_path)
        if "HKEY_LOCAL_MACHINE" in key_path:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path.replace("HKEY_LOCAL_MACHINE\\", ""), 0, winreg.KEY_SET_VALUE)
        elif "HKEY_CURRENT_USER" in key_path:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path.replace("HKEY_CURRENT_USER\\", ""), 0, winreg.KEY_SET_VALUE)
        else:
            return False
        winreg.SetValueEx(key, value_name, 0, value_type, value_data)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        print(f"Error al modificar el registro: {e}")
        return False

def get_registry_value(key_path, value_name):
    """Obtiene un valor del registro de Windows"""
    try:
        if "HKEY_LOCAL_MACHINE" in key_path:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path.replace("HKEY_LOCAL_MACHINE\\", ""), 0, winreg.KEY_READ)
        elif "HKEY_CURRENT_USER" in key_path:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path.replace("HKEY_CURRENT_USER\\", ""), 0, winreg.KEY_READ)
        else:
            return None
        value, regtype = winreg.QueryValueEx(key, value_name)
        winreg.CloseKey(key)
        return value
    except:
        return None
