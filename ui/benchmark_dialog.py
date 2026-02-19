from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QTextEdit, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import threading

from features.benchmarks import (CPUBenchmark, RAMBenchmark, DiskBenchmark, 
                                 NetworkBenchmark, BenchmarkManager)

class BenchmarkThread(QThread):
    """Thread para ejecutar benchmarks sin bloquear UI"""
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(str, dict)  # benchmark_name, result
    
    def __init__(self, benchmark_func, benchmark_name):
        super().__init__()
        self.benchmark_func = benchmark_func
        self.benchmark_name = benchmark_name
    
    def run(self):
        try:
            result = self.benchmark_func(self.log_callback)
            self.finished_signal.emit(self.benchmark_name, result)
        except Exception as e:
            self.log_signal.emit(f"[ERR] Error en benchmark: {str(e)}")
            self.finished_signal.emit(self.benchmark_name, {})
    
    def log_callback(self, message):
        self.log_signal.emit(message)


class BenchmarkDialog(QDialog):
    """Ventana de benchmarks con glassmorfismo y gráficas profesionales"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("System Benchmarks - Analisis de Rendimiento")
        self.setGeometry(100, 100, 1500, 850)
        self.setModal(True)
        
        self.current_thread = None
        self.benchmark_results = {}
        
        self.init_ui()
        self.load_historical_data()
    
    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # Panel izquierdo - Selección de benchmarks
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Panel central - Gráficas
        center_panel = self.create_center_panel()
        main_layout.addWidget(center_panel, 3)
        
        # Panel derecho - Log y controles
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
        # Aplicar estilos con glassmorfismo
        self.setStyleSheet("""
            QDialog {
                background-color: #0f0a1f;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
            }
            QPushButton {
                background: rgba(98, 0, 234, 0.5);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(124, 77, 255, 0.7);
            }
            QListWidget {
                background: rgba(20, 20, 40, 0.6);
                color: #ffffff;
                border: 2px solid rgba(98, 0, 234, 0.5);
                border-radius: 10px;
            }
            QListWidget::item:selected {
                background: rgba(98, 0, 234, 0.6);
            }
            QTextEdit {
                background: rgba(15, 20, 40, 0.7);
                color: #00ff88;
                border: 2px solid rgba(98, 0, 234, 0.5);
                border-radius: 10px;
                font-family: 'Consolas', monospace;
            }
        """)
    
    def create_left_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título sin emoji
        title = QLabel("Categorías Benchmark")
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Lista de benchmarks sin emojis
        self.benchmark_list = QListWidget()
        self.benchmark_list.addItems([
            "BENCHMARK GENERAL",
            "CPU - Single Core",
            "CPU - Multi Core",
            "RAM - Write Speed",
            "RAM - Read Speed",
            "Disk - Sequential Write",
            "Disk - Sequential Read",
            "Network - Latency"
        ])
        self.benchmark_list.currentRowChanged.connect(self.on_benchmark_selected)
        layout.addWidget(self.benchmark_list)
        
        # Botones sin emojis
        self.run_btn = QPushButton("EJECUTAR BENCHMARK")
        self.run_btn.clicked.connect(self.run_selected_benchmark)
        self.run_btn.setMinimumHeight(45)
        layout.addWidget(self.run_btn)
        
        self.run_all_btn = QPushButton("EJECUTAR TODOS")
        self.run_all_btn.clicked.connect(self.run_all_benchmarks)
        self.run_all_btn.setMinimumHeight(45)
        layout.addWidget(self.run_all_btn)
        
        self.delete_btn = QPushButton("BORRAR BENCHMARK")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: rgba(229, 57, 53, 0.4);
                border: 2px solid rgba(244, 67, 54, 0.6);
            }
            QPushButton:hover {
                background: rgba(244, 67, 54, 0.6);
                border: 2px solid rgba(255, 82, 82, 0.8);
            }
        """)
        self.delete_btn.clicked.connect(self.delete_selected_benchmark)
        self.delete_btn.setMinimumHeight(45)
        layout.addWidget(self.delete_btn)
        
        panel.setLayout(layout)
        return panel
    
    def create_center_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título sin emoji
        title = QLabel("Resultados Visuales")
        title.setFont(QFont("Arial", 15, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Matplotlib canvas
        self.figure = Figure(figsize=(10, 7), facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Inicializar gráfica vacía
        self.ax = self.figure.add_subplot(111, facecolor='rgba(15, 28, 46, 0.6)')
        self.ax.set_title("Selecciona un benchmark para comenzar", 
                         color='#ffffff', fontsize=16, fontweight='bold', pad=20)
        self.ax.tick_params(colors='#ffffff', labelsize=10)
        self.ax.grid(True, alpha=0.2, color='#6200ea', linestyle='--')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('rgba(98, 0, 234, 0.6)')
            spine.set_linewidth(2)
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Título sin emoji
        title = QLabel("Log de Ejecución")
        title.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Log
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.append("[INFO] Sistema de Benchmarks iniciado")
        self.log_text.append("[INFO] Selecciona un benchmark para comenzar")
        self.log_text.append("")
        layout.addWidget(self.log_text)
        
        # Botón limpiar
        self.clear_btn = QPushButton("LIMPIAR LOG")
        self.clear_btn.clicked.connect(self.log_text.clear)
        self.clear_btn.setMinimumHeight(40)
        layout.addWidget(self.clear_btn)
        
        panel.setLayout(layout)
        return panel
    
    def add_log(self, message):
        """Añade mensaje al log"""
        self.log_text.append(message)
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def on_benchmark_selected(self, index):
        """Cuando se selecciona un benchmark, mostrar su gráfica"""
        if index < 0:
            return
        
        benchmark_name = self.get_benchmark_name(index)
        self.update_graph(benchmark_name)
    
    def get_benchmark_name(self, index):
        """Mapea índice a nombre de benchmark"""
        names = [
            "general", "cpu_single", "cpu_multi", "ram_write", "ram_read",
            "disk_write", "disk_read", "network_latency"
        ]
        return names[index] if index < len(names) else ""
    
    def delete_selected_benchmark(self):
        """Borra los resultados del benchmark seleccionado"""
        current_row = self.benchmark_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona un benchmark primero")
            return
        
        benchmark_name = self.get_benchmark_name(current_row)
        
        reply = QMessageBox.question(self, 'Confirmar Borrado',
                                     f'¿Estás seguro de borrar todos los resultados de {self.benchmark_list.currentItem().text()}?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Cargar resultados
            results = BenchmarkManager.load_results()
            
            if benchmark_name in results:
                del results[benchmark_name]
                
                # Guardar
                import json
                with open(BenchmarkManager.RESULTS_FILE, 'w') as f:
                    json.dump(results, f, indent=2)
                
                self.add_log(f"[OK] Benchmark {benchmark_name} borrado")
                
                # Actualizar gráfica
                self.update_graph(benchmark_name)
            else:
                QMessageBox.information(self, "Información", "No hay resultados para borrar")
    
    def run_selected_benchmark(self):
        """Ejecuta el benchmark seleccionado"""
        current_row = self.benchmark_list.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Advertencia", "Selecciona un benchmark primero")
            return
        
        if self.current_thread and self.current_thread.isRunning():
            QMessageBox.warning(self, "Advertencia", "Ya hay un benchmark ejecutándose")
            return
        
        benchmark_name = self.get_benchmark_name(current_row)
        benchmark_func = self.get_benchmark_function(current_row)
        
        self.add_log(f"[>>] Iniciando {self.benchmark_list.currentItem().text()}...")
        
        # Deshabilitar botones
        self.run_btn.setEnabled(False)
        self.run_all_btn.setEnabled(False)
        
        # Crear y ejecutar thread
        self.current_thread = BenchmarkThread(benchmark_func, benchmark_name)
        self.current_thread.log_signal.connect(self.add_log)
        self.current_thread.finished_signal.connect(self.on_benchmark_finished)
        self.current_thread.start()
    
    def get_benchmark_function(self, index):
        """Obtiene la función de benchmark según el índice"""
        functions = [
            self.run_general_benchmark,  # Benchmark general
            CPUBenchmark.run_single_core,
            CPUBenchmark.run_multi_core,
            RAMBenchmark.run_write_test,
            RAMBenchmark.run_read_test,
            DiskBenchmark.run_sequential_write,
            DiskBenchmark.run_sequential_read,
            NetworkBenchmark.run_latency_test
        ]
        return functions[index] if index < len(functions) else None
    
    def run_general_benchmark(self, progress_callback=None):
        """Ejecuta todos los benchmarks y calcula un promedio general"""
        if progress_callback:
            progress_callback("[>>] Ejecutando suite completa de benchmarks...")
        
        all_scores = []
        
        # Ejecutar cada benchmark
        benchmarks = [
            ("CPU Single-Core", CPUBenchmark.run_single_core),
            ("CPU Multi-Core", CPUBenchmark.run_multi_core),
            ("RAM Write", RAMBenchmark.run_write_test),
            ("RAM Read", RAMBenchmark.run_read_test),
            ("Disk Write", DiskBenchmark.run_sequential_write),
            ("Disk Read", DiskBenchmark.run_sequential_read)
        ]
        
        for name, bench_func in benchmarks:
            try:
                if progress_callback:
                    progress_callback(f"[...] Ejecutando {name}...")
                result = bench_func(progress_callback)
                
                # Normalizar scores (CPU y RAM/Disk tienen diferentes escalas)
                if "score" in result:
                    # CPU benchmark - operaciones por segundo
                    normalized_score = result["score"] / 100  # Normalizar a escala 0-100
                elif "speed" in result:
                    # RAM/Disk - MB/s
                    normalized_score = result["speed"] / 10  # Normalizar a escala similar
                else:
                    normalized_score = 50  # Default
                
                all_scores.append(normalized_score)
                
                if progress_callback:
                    progress_callback(f"[OK] {name} completado")
            except Exception as e:
                if progress_callback:
                    progress_callback(f"[ERR] Error en {name}: {str(e)}")
        
        # Calcular promedio
        if all_scores:
            average_score = sum(all_scores) / len(all_scores)
            if progress_callback:
                progress_callback(f"[OK] Score General: {average_score:.1f}/100")
            
            return {
                "score": average_score,
                "detail": f"Promedio de {len(all_scores)} benchmarks"
            }
        
        return {"score": 0, "detail": "No se pudo calcular"}
    
    def on_benchmark_finished(self, benchmark_name, result):
        """Callback cuando termina un benchmark"""
        # Guardar resultado
        if result:
            self.benchmark_results[benchmark_name] = result
            BenchmarkManager.save_result(benchmark_name, result)
            self.add_log(f"[OK] Benchmark completado y guardado")
            
            # Actualizar gráfica
            self.update_graph(benchmark_name)
        
        # Rehabilitar botones
        self.run_btn.setEnabled(True)
        self.run_all_btn.setEnabled(True)
    
    def run_all_benchmarks(self):
        """Ejecuta todos los benchmarks secuencialmente"""
        reply = QMessageBox.question(self, 'Ejecutar Todos',
                                     'Esto ejecutará todos los benchmarks secuencialmente.\\n'
                                     'Puede tomar varios minutos.\\n\\n'
                                     '¿Deseas continuar?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.add_log("[INFO] Iniciando suite completa de benchmarks...")
            # Por ahora mostrar mensaje (implementación completa requiere coordinación de threads)
            QMessageBox.information(self, "Información", 
                                   "Ejecutando todos los benchmarks...\\n"
                                   "Por favor ejecuta cada uno individualmente por ahora.")
    
    def load_historical_data(self):
        """Carga datos históricos de benchmarks"""
        self.benchmark_results = BenchmarkManager.get_latest_results()
        if self.benchmark_results:
            self.add_log(f"[INFO] Cargados {len(self.benchmark_results)} resultados previos")
    
    def update_graph(self, benchmark_name):
        """Actualiza la gráfica con datos del benchmark"""
        self.ax.clear()
        
        # Obtener resultados históricos
        all_results = BenchmarkManager.load_results()
        
        if benchmark_name not in all_results or not all_results[benchmark_name]:
            self.ax.set_title(f"No hay datos para {benchmark_name}", color='white')
            self.ax.set_facecolor('#16213e')
            self.canvas.draw()
            return
        
        results = all_results[benchmark_name]
        
        # Extraer datos
        timestamps = [r["timestamp"][:10] for r in results]
        
        # Determinar qué valor graficar según el benchmark
        if benchmark_name == "general":
            values = [r["result"]["score"] for r in results]
            ylabel = "Score General (0-100)"
            title = "Benchmark General - Rendimiento Global"
        elif benchmark_name in ["cpu_single", "cpu_multi"]:
            values = [r["result"]["score"] for r in results]
            ylabel = "Operaciones por segundo"
            title = "Rendimiento CPU"
        elif benchmark_name in ["ram_write", "ram_read", "disk_write", "disk_read"]:
            values = [r["result"]["speed"] for r in results]
            ylabel = "MB/s"
            title = f"{benchmark_name.replace('_', ' ').title()} Speed"
        elif benchmark_name == "network_latency":
            values = [r["result"]["avg"] for r in results]
            ylabel = "Latencia (μs)"
            title = "Network Latency"
        else:
            values = []
            ylabel = ""
            title = benchmark_name
        
        # Crear gráfica
        self.ax.plot(range(len(values)), values, 'o-', color='#7c4dff', linewidth=2, markersize=8)
        self.ax.set_title(title, color='white', fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Ejecuciones", color='white')
        self.ax.set_ylabel(ylabel, color='white')
        self.ax.grid(True, alpha=0.3, color='#555')
        self.ax.tick_params(colors='white')
        self.ax.set_facecolor('#16213e')
        
        for spine in self.ax.spines.values():
            spine.set_edgecolor('#6200ea')
        
        # Añadir línea promedio
        if len(values) > 1:
            avg_value = sum(values) / len(values)
            self.ax.axhline(y=avg_value, color='#ffb300', linestyle='--', alpha=0.7, linewidth=2, label=f'Promedio: {avg_value:.1f}')
            self.ax.legend(loc='upper left', facecolor='#16213e', edgecolor='#6200ea', labelcolor='white')
        
        # Añadir indicadores de mejora (+/-%) en cada punto
        for i in range(1, len(values)):
            prev_value = values[i-1]
            curr_value = values[i]
            
            if prev_value > 0:
                # Para latencia, menor es mejor, invertir el cálculo
                if benchmark_name == "network_latency":
                    percent_change = ((prev_value - curr_value) / prev_value) * 100
                else:
                    percent_change = ((curr_value - prev_value) / prev_value) * 100
                
                # Color basado en mejora/degradación
                color = '#00ff00' if percent_change > 0 else '#ff5252'
                symbol = '+' if percent_change > 0 else ''
                
                # Añadir texto sobre el punto
                self.ax.text(i, curr_value, f'{symbol}{percent_change:.1f}%', 
                           color=color, fontsize=9, fontweight='bold',
                           ha='center', va='bottom')
        
        # Valor actual
        if values:
            latest = values[-1]
            self.ax.plot(len(values)-1, latest, 'o', color='#00ff00', markersize=12)
        
        self.canvas.draw()
