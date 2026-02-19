import time
from utils.system import run_command_in_shell

class SystemOptimizer:
    """Módulo de lógica de optimización del sistema"""
    
    @staticmethod
    def run_optimization(logger_func):
        """Ejecuta el proceso de optimización completo"""
        logger_func("[>>] INICIANDO PROCESO DE OPTIMIZACIÓN COMPLETO")
        logger_func("[>>] Preparando módulos de optimización del sistema...")
        
        for i in range(3):
            logger_func(f"[...] Cargando módulos de optimización [{'■' * (i+1)}{'□' * (2-i)}]")
            time.sleep(0.3)
        
        reg_commands = [
            ('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\PowerThrottling" /v "PowerThrottlingOff" /t REG_DWORD /d 1 /f', "[>>] Desactivando Power Throttling"),
            ('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "SystemResponsiveness" /t REG_DWORD /d 10 /f', "[>>] Ajustando SystemResponsiveness"),
            ('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NetworkThrottlingIndex" /t REG_DWORD /d 4294967295 /f', "[>>] Optimizando NetworkThrottlingIndex"),
            ('reg add "HKCU\\System\\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f', "[>>] Desactivando GameDVR"),
            ('reg add "HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f', "[>>] Desactivando AppCapture"),
            ('reg add "HKCU\\Control Panel\\Desktop" /v "AutoEndTasks" /t REG_SZ /d "1" /f', "[>>] Configurando AutoEndTasks"),
            ('reg add "HKCU\Control Panel\\Desktop" /v "HungAppTimeout" /t REG_SZ /d "1000" /f', "[>>] Ajustando HungAppTimeout"),
            ('reg add "HKCU\\Control Panel\\Desktop" /v "WaitToKillAppTimeout" /t REG_SZ /d "3000" /f', "[>>] Configurando WaitToKillAppTimeout"),
            ('reg add "HKCU\\Control Panel\\Desktop" /v "LowLevelHooksTimeout" /t REG_SZ /d "1000" /f', "[>>] Ajustando LowLevelHooksTimeout"),
            ('reg add "HKCU\\Control Panel\\Desktop" /v "MenuShowDelay" /t REG_SZ /d "0" /f', "[>>] Eliminando delay en menús"),
            ('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control" /v "WaitToKillServiceTimeout" /t REG_SZ /d "2000" /f', "[>>] Configurando WaitToKillServiceTimeout"),
            ('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Schedule\\Maintenance" /v "MaintenanceDisabled" /t REG_DWORD /d 1 /f', "[>>] Desactivando mantenimiento automático"),
            ('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power" /v "HibernateEnabled" /t REG_DWORD /d 0 /f', "[>>] Desactivando hibernación"),
            ('bcdedit /set disabledynamictick yes', "[>>] Configurando disabledynamictick"),
            ('bcdedit /deletevalue useplatformclock', "[>>] Eliminando useplatformclock"),
            ('bcdedit /set useplatformtick yes', "[>>] Configurando useplatformtick")
        ]
        
        total_commands = len(reg_commands)
        executed_commands = 0
        
        for i, (cmd, desc) in enumerate(reg_commands, 1):
            logger_func(f"[RUN] Ejecutando: {desc}")
            
            progress = int(i/total_commands * 100)
            progress_bar = f"[{'█' * int(progress/5)}{'░' * (20 - int(progress/5))}]"
            logger_func(f"[PROG] {progress_bar} {progress}%")
            
            success = run_command_in_shell(cmd)
            if success:
                logger_func(f"[OK] Comando completado exitosamente")
                executed_commands += 1
            else:
                logger_func(f"[WARN] Advertencia en comando")
            time.sleep(0.2)
        
        logger_func("[OK] OPTIMIZACIÓN COMPLETADA EXITOSAMENTE")
        logger_func(f"[INFO] Comandos ejecutados: {executed_commands}/{total_commands}")
        logger_func("[INFO] Sistema optimizado para máximo rendimiento")
        
        return True
