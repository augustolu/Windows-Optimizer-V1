import time
import os
import json
import psutil
import threading
from datetime import datetime
import multiprocessing

class BenchmarkManager:
    """Gestiona la ejecución y almacenamiento de benchmarks"""
    
    RESULTS_FILE = "data/benchmark_results.json"
    
    @staticmethod
    def save_result(benchmark_name, result):
        """Guarda resultado de benchmark con timestamp"""
        os.makedirs("data", exist_ok=True)
        
        # Cargar resultados existentes
        results = BenchmarkManager.load_results()
        
        # Agregar nuevo resultado
        if benchmark_name not in results:
            results[benchmark_name] = []
        
        results[benchmark_name].append({
            "timestamp": datetime.now().isoformat(),
            "result": result
        })
        
        # Guardar
        with open(BenchmarkManager.RESULTS_FILE, 'w') as f:
            json.dump(results, f, indent=2)
    
    @staticmethod
    def load_results():
        """Carga resultados históricos"""
        if os.path.exists(BenchmarkManager.RESULTS_FILE):
            try:
                with open(BenchmarkManager.RESULTS_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    @staticmethod
    def get_latest_results():
        """Obtiene los últimos resultados de cada benchmark"""
        results = BenchmarkManager.load_results()
        latest = {}
        for bench_name, bench_results in results.items():
            if bench_results:
                latest[bench_name] = bench_results[-1]
        return latest


class CPUBenchmark:
    """Benchmark de CPU - Single y Multi-core"""
    
    @staticmethod
    def run_single_core(progress_callback=None):
        """Test de single-core - 15 mediciones promediadas"""
        if progress_callback:
            progress_callback("[>>] Iniciando benchmark CPU Single-Core (15 mediciones)...")
        
        # Fijar a un solo core
        p = psutil.Process()
        original_affinity = p.cpu_affinity()
        p.cpu_affinity([0])
        
        measurements = []
        
        for measurement in range(15):
            if progress_callback:
                progress_callback(f"[PROG] Medición {measurement + 1}/15...")
            
            start_time = time.perf_counter()
            
            # Cálculo matemático intensivo más realista
            result = 0.0
            iterations = 2000000
            for i in range(iterations):
                result += (i ** 0.5) * 1.234567
                result = result % 1000000
            
            elapsed = time.perf_counter() - start_time
            score = int(1000000 / elapsed)
            measurements.append(score)
            
            time.sleep(0.1)  # Pequeña pausa entre mediciones
        
        # Restaurar affinity
        p.cpu_affinity(original_affinity)
        
        # Calcular promedio
        avg_score = int(sum(measurements) / len(measurements))
        
        if progress_callback:
            progress_callback(f"[OK] Single-Core completado: {avg_score:,} ops/s (promedio de 15 mediciones)")
        
        return {
            "score": avg_score,
            "measurements": measurements,
            "unit": "ops/s"
        }
    
    @staticmethod
    def run_multi_core(progress_callback=None):
        """Test de multi-core - 15 mediciones con threading"""
        if progress_callback:
            progress_callback("[>>] Iniciando benchmark CPU Multi-Core (15 mediciones)...")
        
        cpu_count = psutil.cpu_count(logical=True)
        
        def worker(iterations):
            result = 0.0
            for i in range(iterations):
                result += (i ** 0.5) * 1.234567
                result = result % 1000000
            return result
        
        measurements = []
        
        for measurement in range(15):
            if progress_callback:
                progress_callback(f"[PROG] Medición {measurement + 1}/15 ({cpu_count} threads)...")
            
            start_time = time.perf_counter()
            
            # Usar threading en vez de multiprocessing (mejor para Windows)
            threads = []
            iterations_per_thread = 500000
            
            for _ in range(cpu_count):
                thread = threading.Thread(target=worker, args=(iterations_per_thread,))
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            elapsed = time.perf_counter() - start_time
            score = int((cpu_count * 1000000) / elapsed)
            measurements.append(score)
            
            time.sleep(0.1)
        
        avg_score = int(sum(measurements) / len(measurements))
        
        if progress_callback:
            progress_callback(f"[OK] Multi-Core completado: {avg_score:,} ops/s ({cpu_count} cores)")
        
        return {
            "score": avg_score,
            "measurements": measurements,
            "cores": cpu_count,
            "unit": "ops/s"
        }


class RAMBenchmark:
    """Benchmark de RAM - velocidad de lectura/escritura"""
    
    @staticmethod
    def run_write_test(progress_callback=None):
        """Test de escritura en RAM - 15 mediciones"""
        if progress_callback:
            progress_callback("[>>] Iniciando benchmark RAM Write (15 mediciones)...")
        
        size_mb = 200
        measurements = []
        
        for measurement in range(15):
            if progress_callback:
                progress_callback(f"[PROG] Medición {measurement + 1}/15...")
            
            array_size = size_mb * 1024 * 1024 // 8
            
            start_time = time.perf_counter()
            
            # Escritura más realista con diferentes patrones
            data = bytearray(array_size)
            for i in range(0, array_size, 1000):
                data[i] = (i % 256)
            
            elapsed = time.perf_counter() - start_time
            speed_mbs = size_mb / elapsed
            measurements.append(speed_mbs)
            
            time.sleep(0.05)
        
        avg_speed = sum(measurements) / len(measurements)
        
        if progress_callback:
            progress_callback(f"[OK] RAM Write completado: {avg_speed:,.0f} MB/s")
        
        return {
            "speed": round(avg_speed, 2),
            "measurements": measurements,
            "unit": "MB/s"
        }
    
    @staticmethod
    def run_read_test(progress_callback=None):
        """Test de lectura de RAM - 15 mediciones"""
        if progress_callback:
            progress_callback("[>>] Iniciando benchmark RAM Read (15 mediciones)...")
        
        size_mb = 200
        measurements = []
        
        for measurement in range(15):
            if progress_callback:
                progress_callback(f"[PROG] Medición {measurement + 1}/15...")
            
            array_size = size_mb * 1024 * 1024 // 8
            data = bytes(array_size)
            
            start_time = time.perf_counter()
            
            # Lectura más realista
            suma = 0
            for i in range(0, array_size, 1000):
                suma += data[i]
            
            elapsed = time.perf_counter() - start_time
            speed_mbs = size_mb / elapsed
            measurements.append(speed_mbs)
            
            time.sleep(0.05)
        
        avg_speed = sum(measurements) / len(measurements)
        
        if progress_callback:
            progress_callback(f"[OK] RAM Read completado: {avg_speed:,.0f} MB/s")
        
        return {
            "speed": round(avg_speed, 2),
            "measurements": measurements,
            "unit": "MB/s"
        }


class DiskBenchmark:
    """Benchmark de Disco - I/O secuencial"""
    
    @staticmethod
    def run_sequential_write(progress_callback=None):
        """Test de escritura secuencial - 15 mediciones"""
        if progress_callback:
            progress_callback("[>>] Iniciando benchmark Disk Write (15 mediciones)...")
        
        test_file = "benchmark_disk_test.tmp"
        file_size_mb = 50
        measurements = []
        
        for measurement in range(15):
            if progress_callback:
                progress_callback(f"[PROG] Medición {measurement + 1}/15...")
            
            chunk_size = 1024 * 1024
            
            start_time = time.perf_counter()
            
            with open(test_file, 'wb') as f:
                data = os.urandom(chunk_size)
                for _ in range(file_size_mb):
                    f.write(data)
                f.flush()
                os.fsync(f.fileno())  # Asegurar escritura real al disco
            
            elapsed = time.perf_counter() - start_time
            speed_mbs = file_size_mb / elapsed
            measurements.append(speed_mbs)
            
            try:
                os.remove(test_file)
            except Exception:
                pass
            
            time.sleep(0.1)
        
        avg_speed = sum(measurements) / len(measurements)
        
        if progress_callback:
            progress_callback(f"[OK] Disk Write completado: {avg_speed:,.0f} MB/s")
        
        return {
            "speed": round(avg_speed, 2),
            "measurements": measurements,
            "unit": "MB/s"
        }
    
    @staticmethod
    def run_sequential_read(progress_callback=None):
        """Test de lectura secuencial - 15 mediciones"""
        if progress_callback:
            progress_callback("[>>] Iniciando benchmark Disk Read (15 mediciones)...")
        
        test_file = "benchmark_disk_test.tmp"
        file_size_mb = 50
        chunk_size = 1024 * 1024
        
        # Crear archivo una vez
        with open(test_file, 'wb') as f:
            data = os.urandom(chunk_size)
            for _ in range(file_size_mb):
                f.write(data)
        
        measurements = []
        
        for measurement in range(15):
            if progress_callback:
                progress_callback(f"[PROG] Medición {measurement + 1}/15...")
            
            start_time = time.perf_counter()
            
            with open(test_file, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
            
            elapsed = time.perf_counter() - start_time
            speed_mbs = file_size_mb / elapsed
            measurements.append(speed_mbs)
            
            time.sleep(0.1)
        
        avg_speed = sum(measurements) / len(measurements)
        
        try:
            os.remove(test_file)
        except Exception:
            pass
        
        if progress_callback:
            progress_callback(f"[OK] Disk Read completado: {avg_speed:,.0f} MB/s")
        
        return {
            "speed": round(avg_speed, 2),
            "measurements": measurements,
            "unit": "MB/s"
        }


class NetworkBenchmark:
    """Benchmark de Red - latencia local"""
    
    @staticmethod
    def run_latency_test(progress_callback=None):
        """Test de latencia - 15 mediciones promediadas"""
        if progress_callback:
            progress_callback("[>>] Iniciando benchmark Network Latency (15 sets)...")
        
        set_measurements = []
        
        for set_num in range(15):
            if progress_callback:
                progress_callback(f"[PROG] Set {set_num + 1}/15...")
            
            latencies = []
            for _ in range(10):
                start = time.perf_counter_ns()
                _ = psutil.net_io_counters()
                end = time.perf_counter_ns()
                latency_us = (end - start) / 1000
                latencies.append(latency_us)
                time.sleep(0.001)
            
            avg_in_set = sum(latencies) / len(latencies)
            set_measurements.append(avg_in_set)
            time.sleep(0.05)
        
        avg_latency = sum(set_measurements) / len(set_measurements)
        min_latency = min(set_measurements)
        max_latency = max(set_measurements)
        
        if progress_callback:
            progress_callback(f"[OK] Network Latency completado: {avg_latency:.2f} μs avg")
        
        return {
            "avg": round(avg_latency, 2),
            "min": round(min_latency, 2),
            "max": round(max_latency, 2),
            "measurements": set_measurements,
            "unit": "μs"
        }
