import os
import shutil
import time
import datetime
import psutil
import stat
import statistics
import winreg
from datetime import datetime as dt

class SystemMaintenance:
    """Módulo de mantenimiento del sistema"""
    
    @staticmethod
    def run_maintenance(logger_func):
        """Ejecuta el mantenimiento completo"""
        logger_func("[>>] INICIANDO MANTENIMIENTO COMPLETO DEL SISTEMA")

        log_filename = f"mantenimiento_{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt"
        logfile = os.path.join(os.getcwd(), log_filename)
        
        with open(logfile, "w", encoding="utf-8") as log:
            log.write("===== INFORME DE MANTENIMIENTO =====\\n")
            log.write(f"Fecha: {dt.now()}\\n\\n")

            logger_func("[>>] Limpiando archivos temporales...")
            SystemMaintenance._clean_temp_files(logger_func, log)

            logger_func("[>>] Recolectando información del sistema...")
            SystemMaintenance._collect_system_info(logger_func, log)

            logger_func("[>>] Ejecutando benchmark de disco...")
            SystemMaintenance._run_disk_benchmark(logger_func, log)

            logger_func("[>>] Ejecutando test de latencia en core 0 (10 pruebas)...")
            SystemMaintenance._run_latency_test(logger_func, log)

            logger_func("[>>] Obteniendo procesos más pesados...")
            SystemMaintenance._get_heavy_processes(logger_func, log)

            logger_func("[>>] Listando programas en Startup...")
            SystemMaintenance._list_startup_programs(logger_func, log)

        logger_func("[OK] MANTENIMIENTO COMPLETADO EXITOSAMENTE")
        logger_func(f"[INFO] Log guardado en {log_filename}")
        
        return log_filename

    @staticmethod
    def _clean_temp_files(logger_func, log_file):
        total_deleted = 0
        total_skipped = 0
        skipped_files = []
        temp_paths = [
            os.expandvars(r"%TEMP%"),
            os.expandvars(r"%WINDIR%\\Temp"),
            os.expandvars(r"%LOCALAPPDATA%\\Temp")
        ]

        for path in temp_paths:
            if not os.path.exists(path):
                logger_func(f"[WARN] Directorio no encontrado: {path}")
                log_file.write(f"Directorio no encontrado: {path}\\n")
                continue

            try:
                for root, dirs, files in os.walk(path, topdown=True):
                    # Intentar eliminar directorios vacíos
                    for dir_name in dirs:
                        dir_path = os.path.join(root, dir_name)
                        try:
                            shutil.rmtree(dir_path, ignore_errors=True)
                            total_deleted += 1
                        except Exception:
                            pass

                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            try:
                                os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)
                            except Exception:
                                pass

                            os.remove(file_path)
                            total_deleted += 1
                            if total_deleted % 500 == 0:
                                logger_func(f"[INFO] Eliminados {total_deleted} archivos...")
                        except PermissionError as e:
                            skipped_files.append((file_path, f"Permiso denegado: {str(e)}"))
                            total_skipped += 1
                        except OSError as e:
                            skipped_files.append((file_path, f"Error del sistema: {str(e)}"))
                            total_skipped += 1
                        except Exception as e:
                            skipped_files.append((file_path, f"Error: {str(e)}"))
                            total_skipped += 1
            except Exception as e:
                logger_func(f"[WARN] Error al acceder al directorio {root}: {str(e)}")
                log_file.write(f"Error al acceder al directorio {root}: {str(e)}\\n")

        logger_func(f"[INFO] RESUMEN: {total_deleted} archivos/directorios eliminados, {total_skipped} omitidos")
        log_file.write(f"Archivos y directorios eliminados: {total_deleted}\\n")
        log_file.write(f"Archivos omitidos: {total_skipped}\\n")

    @staticmethod
    def _collect_system_info(logger_func, log_file):
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        log_file.write("\\n--- Estado del sistema ---\\n")
        log_file.write(f"CPU en uso: {cpu_percent}%\\n")
        log_file.write(f"RAM en uso: {ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)\\n")
        log_file.write(f"Disco libre: {disk.free // (1024**3)}GB de {disk.total // (1024**3)}GB\\n")

    @staticmethod
    def _run_disk_benchmark(logger_func, log_file):
        testfile = "bench_temp.bin"
        size_mb = 50
        data = os.urandom(1024 * 1024)

        try:
            start_time = time.time()
            with open(testfile, "wb") as f:
                for _ in range(size_mb):
                    f.write(data)
            write_time = time.time() - start_time

            start_time = time.time()
            with open(testfile, "rb") as f:
                while f.read(1024 * 1024):
                    pass
            read_time = time.time() - start_time

            os.remove(testfile)

            log_file.write("\\n--- Benchmark Disco ---\\n")
            log_file.write(f"Vel. escritura: {size_mb / write_time:.2f} MB/s\\n")
            log_file.write(f"Vel. lectura: {size_mb / read_time:.2f} MB/s\\n")
        except Exception as e:
            logger_func(f"[ERR] Error en benchmark: {e}")

    @staticmethod
    def _run_latency_test(logger_func, log_file):
        log_file.write("\\n--- Latencia Core 0 (10 Pruebas) ---\\n")
        
        p = psutil.Process()
        original_affinity = p.cpu_affinity()
        p.cpu_affinity([0])
        deltas = []

        try:
            for i in range(10):
                start = time.perf_counter_ns()
                _ = sum(range(500))
                end = time.perf_counter_ns()
                latency = end - start
                deltas.append(latency)
                logger_func(f"[TEST] Chequeo {i+1}: {latency} ns")
                log_file.write(f"Chequeo {i+1}: {latency} ns\\n")
                log_file.flush()
                time.sleep(0.5)
        except Exception as e:
            logger_func(f"[ERR] Error en latencia: {e}")
        finally:
            p.cpu_affinity(original_affinity)

        if deltas:
            avg_lat = statistics.mean(deltas)
            std_lat = statistics.stdev(deltas) if len(deltas) > 1 else 0
            
            logger_func("\\n[INFO] Análisis de Latencia:")
            logger_func(f"Min: {min(deltas)} ns")
            logger_func(f"Max: {max(deltas)} ns")
            logger_func(f"Promedio: {avg_lat:.2f} ns")
            
            log_file.write("\\nAnálisis de Latencia:\\n")
            log_file.write(f"Min: {min(deltas)} ns\\n")
            log_file.write(f"Max: {max(deltas)} ns\\n")
            log_file.write(f"Promedio: {avg_lat:.2f} ns\\n")
            log_file.write(f"Desviación Estándar: {std_lat:.2f} ns\\n")

    @staticmethod
    def _get_heavy_processes(logger_func, log_file):
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                processes.append(proc.info)
            except:
                continue
        top_procs = sorted(processes, key=lambda p: p['memory_info'].rss if p['memory_info'] else 0, reverse=True)[:5]

        log_file.write("\\n--- Procesos principales ---\\n")
        for p in top_procs:
            mem = p['memory_info'].rss / (1024**2) if p['memory_info'] else 0
            log_file.write(f"{p['name']} (PID {p['pid']}) - CPU {p['cpu_percent']}% - RAM {mem:.2f} MB\\n")

    @staticmethod
    def _list_startup_programs(logger_func, log_file):
        log_file.write("\\n--- Programas en Startup ---\\n")
        startup_keys = [
            (winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run")
        ]
        for root, path in startup_keys:
            try:
                with winreg.OpenKey(root, path) as key:
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(key, i)
                            log_file.write(f"{name}: {value}\\n")
                            i += 1
                        except OSError:
                            break
            except FileNotFoundError:
                continue
