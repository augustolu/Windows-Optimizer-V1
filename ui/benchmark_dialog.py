from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QListWidget, QTextEdit, QMessageBox, QWidget)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPainter, QRadialGradient, QBrush, QColor
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np
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
        
        self.animation_timer = QTimer(self)
        self.animation_progress = 0
        self.animation_target_x = []
        self.animation_target_y = []
        self.animation_line = None
        self.animation_points = None
        self.animation_timer.timeout.connect(self._animate_chart_step)
        
        self.init_ui()
        self.load_historical_data()
    
    def init_ui(self):
        main_layout = QHBoxLayout()
        
        left_panel = self.create_left_panel()
        left_panel.setObjectName("glassPanel")
        main_layout.addWidget(left_panel, 1)
        
        # Panel central - Gráficas
        center_panel = self.create_center_panel()
        center_panel.setObjectName("glassPanel")
        main_layout.addWidget(center_panel, 3)
        
        # Panel derecho - Log y controles
        right_panel = self.create_right_panel()
        right_panel.setObjectName("glassPanel")
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
        # Aplicar estilos con glassmorfismo adaptado al HTML
        self.setStyleSheet("""
            QDialog {
                background-color: transparent;
            }
            #glassPanel {
                background-color: rgba(255, 255, 255, 0.03);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
            }
            QLabel {
                color: #ffffff;
                background: transparent;
                font-family: 'Inter', sans-serif;
            }
            QPushButton {
                background: rgba(255, 255, 255, 0.05);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.1);
                padding: 12px;
                border-radius: 8px;
                font-weight: bold;
                font-family: 'Inter', sans-serif;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            QListWidget {
                background: transparent;
                color: #d1d5db;
                border: none;
                font-family: 'Inter', sans-serif;
                outline: none;
            }
            QListWidget::item {
                background: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
                font-weight: 600;
                font-size: 13px;
            }
            QListWidget::item:hover {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(38, 198, 255, 0.5);
            }
            QListWidget::item:selected {
                background: rgba(191, 0, 255, 0.1);
                border: 1px solid #bf00ff;
                color: white;
                font-weight: bold;
            }
            QTextEdit {
                background: transparent;
                color: #d1d5db;
                border: none;
            }
        """)
        
    def paintEvent(self, event):
        """Dibuja el fondo radial gradient como el CSS de Tailwind"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        gradient = QRadialGradient(self.width() * 0.2, self.height() * 0.2, self.width())
        gradient.setColorAt(0, QColor("#1a1b4b"))
        gradient.setColorAt(0.4, QColor("#0d0e1f"))
        gradient.setColorAt(1, QColor("#000000"))
        
        painter.fillRect(self.rect(), QBrush(gradient))
    
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
        
        # Botones sin emojis adaptados a UI neon
        self.run_btn = QPushButton("EJECUTAR BENCHMARK")
        self.run_btn.setStyleSheet("border: 1px solid rgba(0, 100, 255, 0.5); color: white;")
        self.run_btn.clicked.connect(self.run_selected_benchmark)
        self.run_btn.setMinimumHeight(45)
        layout.addWidget(self.run_btn)
        
        self.run_all_btn = QPushButton("EJECUTAR TODOS")
        self.run_all_btn.setStyleSheet("border: 1px solid rgba(0, 100, 255, 0.5); color: white;")
        self.run_all_btn.clicked.connect(self.run_all_benchmarks)
        self.run_all_btn.setMinimumHeight(45)
        layout.addWidget(self.run_all_btn)
        
        self.delete_btn = QPushButton("BORRAR BENCHMARK")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 50, 50, 0.05);
                border: 1px solid rgba(255, 50, 50, 0.5);
                color: #ffcccc;
            }
            QPushButton:hover {
                background: rgba(255, 50, 50, 0.15);
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
        
        # Matplotlib canvas (usando color oscuro)
        self.figure = Figure(figsize=(10, 7), facecolor='#0d0e1f')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        # Inicializar gráfica vacía
        self.ax = self.figure.add_subplot(111, facecolor='#0d0e1f')
        self.ax.set_title("Selecciona un benchmark para comenzar", 
                         color='#ffffff', fontsize=16, fontweight='bold', pad=20)
        self.ax.tick_params(colors=(255/255, 255/255, 255/255, 0.4), labelsize=10, length=0)
        self.ax.grid(True, alpha=0.1, color='white', linestyle='-')
        for spine in self.ax.spines.values():
            spine.set_visible(False)
        
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
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: rgba(38, 198, 255, 0.1);
                border: 1px solid rgba(38, 198, 255, 0.3);
                color: #dbeafe;
            }
            QPushButton:hover {
                background: rgba(38, 198, 255, 0.2);
            }
        """)
        self.clear_btn.clicked.connect(self.log_text.clear)
        self.clear_btn.setMinimumHeight(40)
        layout.addWidget(self.clear_btn)
        
        panel.setLayout(layout)
        return panel
    
    def add_log(self, message):
        """Añade mensaje al log con estilo HTML y colores definidos"""
        if "[INFO]" in message:
            message = message.replace("[INFO]", "<span style='color:#00ff00; font-weight:bold;'>[INFO]</span>")
        elif "[OK]" in message:
            message = message.replace("[OK]", "<span style='color:#00ff00; font-weight:bold;'>[RESULT]</span>")
        elif "[>>]" in message:
            message = message.replace("[>>]", "<span style='color:#00ff00; font-weight:bold;'>[EXECUTING]</span>")
        elif "[ERR]" in message:
            message = message.replace("[ERR]", "<span style='color:#ff2a2a; font-weight:bold;'>[ERROR]</span>")
        
        # Colorear números al final para matching de resultados
        import re
        message = re.sub(r'([\d\.,]+)$', r"<span style='color:#bf00ff; font-weight:bold;'>\1</span>", message)
            
        styled_msg = f"<div style='color:#d1d5db; font-family:Courier New; font-size:12px; margin-bottom:4px;'>{message}</div>"
        
        self.log_text.append(styled_msg)
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
            self.update_graph(benchmark_name, animate_append=True)
        
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
    
    def update_graph(self, benchmark_name, animate_append=False):
        """Actualiza la gráfica con datos del benchmark"""
        self.ax.clear()
        
        # Obtener resultados históricos
        all_results = BenchmarkManager.load_results()
        
        if benchmark_name not in all_results or not all_results[benchmark_name]:
            self.ax.set_title(f"No hay datos para {benchmark_name}", color='white')
            
            # Limpiar por completo el aspecto visual
            self.ax.set_facecolor('#0d0e1f')
            self.ax.tick_params(colors='none') 
            self.ax.grid(False)
            for spine in self.ax.spines.values():
                spine.set_visible(False)
                
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
        
        # Clean axes spines
        for spine in self.ax.spines.values():
            spine.set_visible(False)
            
        # Configurar animación
        self.animation_progress = 0
        
        x_vals = list(range(len(values)))
        if len(values) >= 3:
            x_arr = np.array(x_vals)
            y_arr = np.array(values)
            x_ext = np.concatenate(([x_arr[0]], x_arr, [x_arr[-1]]))
            y_ext = np.concatenate(([y_arr[0]], y_arr, [y_arr[-1]]))
            
            x_smooth, y_smooth = [], []
            for i in range(len(x_arr) - 1):
                p0, p1, p2, p3 = y_ext[i], y_ext[i+1], y_ext[i+2], y_ext[i+3]
                t = np.linspace(0, 1, 50)
                h00 = 2*t**3 - 3*t**2 + 1
                h10 = t**3 - 2*t**2 + t
                h01 = -2*t**3 + 3*t**2
                h11 = t**3 - t**2
                m0 = 0.5 * (p2 - p0)
                m1 = 0.5 * (p3 - p1)
                y_segment = (h00*p1 + h10*m0 + h01*p2 + h11*m1).tolist()
                x_segment = np.linspace(x_arr[i], x_arr[i+1], 50).tolist()
                
                if i == 0:
                    x_smooth.extend(x_segment)
                    y_smooth.extend(y_segment)
                else:
                    x_smooth.extend(x_segment[1:])
                    y_smooth.extend(y_segment[1:])
            
            self.animation_target_x = x_smooth
            self.animation_target_y = y_smooth
        elif len(values) == 2:
            x_smooth = np.linspace(0, 1, 50).tolist()
            y_smooth = np.linspace(values[0], values[1], 50).tolist()
            self.animation_target_x = x_smooth
            self.animation_target_y = y_smooth
        else:
            self.animation_target_x = x_vals
            self.animation_target_y = values
            
        if animate_append and len(values) > 1:
            self.animation_progress = max(0, (len(values) - 2) * 50)
            self.animation_step_size = 2
        else:
            self.animation_progress = 0
            self.animation_step_size = max(2, len(self.animation_target_x) // 50)
            
        # Draw base chart components immediately
        self.ax.set_title(title, color='white', fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Ejecuciones", color='white')
        self.ax.set_ylabel(ylabel, color='white')
        self.ax.grid(True, alpha=0.1, color='white', linestyle='-')
        self.ax.tick_params(colors=(1,1,1,0.4), length=0)
        self.ax.set_facecolor('none')
        
        # Añadir línea promedio
        if len(values) > 1:
            avg_value = sum(values) / len(values)
            self.ax.axhline(y=avg_value, color='#a78bfa', linestyle='--', alpha=0.6, linewidth=1, label=f'Promedio: {avg_value:.1f}')
            self.ax.legend(loc='upper left', facecolor='#0d0e1f', edgecolor='none', labelcolor='#a78bfa', fontsize=9)
        
        # Añadir indicadores de mejora (+/-%) en cada punto flotante
        for i in range(1, len(values)):
            prev_value = values[i-1]
            curr_value = values[i]
            
            if prev_value > 0:
                if benchmark_name == "network_latency":
                    percent_change = ((prev_value - curr_value) / prev_value) * 100
                else:
                    percent_change = ((curr_value - prev_value) / prev_value) * 100
                
                if percent_change > 0:
                    bbox = dict(boxstyle="square,pad=0.3", fc="#132f1c", ec="#4ade80")
                    color = "#4ade80"
                    symbol = "+"
                    self.ax.plot(i, curr_value, 'o', color='#4ade80', markerfacecolor='#1a1b4b', markeredgewidth=3, markersize=10)
                else:
                    bbox = dict(boxstyle="square,pad=0.3", fc="#330c0c", ec="#ef4444")
                    color = "#ef4444"
                    symbol = ""
                    self.ax.plot(i, curr_value, 'o', color='#ef4444', markerfacecolor='#1a1b4b', markeredgewidth=3, markersize=10)
                
                y_offset = 12 if percent_change > 0 else -20
                self.ax.annotate(f"{symbol}{percent_change:.1f}%", xy=(i, curr_value), xytext=(0, y_offset),
                                 textcoords="offset points", ha='center', va='bottom' if percent_change > 0 else 'top',
                                 color=color, fontsize=9, fontweight='bold', bbox=bbox)
        
        # Prepara objetos animados vacíos
        self.animation_line, = self.ax.plot([], [], '-', color='#bf00ff', linewidth=4)
        self.animation_points, = self.ax.plot([], [], 'o', color='#e9d5ff', markerfacecolor='#1a1b4b', markeredgewidth=2, markersize=8)
        
        # Valor actual
        if values:
            latest = values[-1]
            self.ax.plot(len(values)-1, latest, 'o', color='#00ff00', markersize=12)
            
        self.ax.set_xlim(-0.2, len(values)-0.8 if len(values) > 1 else 1)
        self.ax.set_ylim(min(values) * 0.9 if values else 0, max(values) * 1.1 if values else 1)
        
        self.canvas.draw()
        
        # Iniciar timer para simular animación CSS (100 pasos en ~1000ms = 10ms/paso)
        self.animation_timer.start(10)
        
    def _animate_chart_step(self):
        """Ejecuta un paso de animación del stroke curve"""
        total_points = len(self.animation_target_x)
        self.animation_progress += getattr(self, 'animation_step_size', 2)
        
        if self.animation_progress >= total_points:
            self.animation_progress = total_points
            self.animation_timer.stop()

        idx = self.animation_progress
        if idx == 0:
            return
            
        current_x = self.animation_target_x[:idx]
        current_y = self.animation_target_y[:idx]
        
        self.animation_line.set_data(current_x, current_y)
        
        # Puntos base sólo se dibujan en enteros
        point_x = [x for x in current_x if float(x).is_integer()]
        point_y = [self.animation_target_y[self.animation_target_x.index(x)] for x in point_x]
        
        self.animation_points.set_data(point_x, point_y)
        
        self.canvas.draw_idle()
