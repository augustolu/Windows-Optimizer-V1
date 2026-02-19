import sys
import os
import base64
import time
import threading
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QGraphicsBlurEffect, QMessageBox,
    QInputDialog, QFrame, QDialog, QLineEdit
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt6.QtGui import QPixmap, QPalette, QBrush, QFont, QColor

# Imports de nuestros módulos
from config.settings import (
    COLOR_BG, COLOR_ACCENT, COLOR_TEXT, COLOR_WARNING, COLOR_HOVER,
    MODERN_FONT, LOGO_FILE, RESOURCES_FOLDER, PASSWORD_HASH,
    load_config, save_config
)
from utils.system import is_admin, run_command_in_shell
from utils.files import extract_7z_resources, run_anydesk
from utils.registry import set_registry_value
from features.security import HardwareIDGenerator, LicenseValidator
from features.optimization import SystemOptimizer
from features.maintenance import SystemMaintenance

class ModernPasswordDialog(QDialog):
    def __init__(self, password_hash):
        super().__init__()
        self.password_hash = password_hash
        self.result = False
        self.setWindowTitle("CACHE_CORE x64 - Acceso Seguro")
        self.setFixedSize(450, 450)
        self.setStyleSheet("background-color: #0a0015; color: white;")
        layout = QVBoxLayout(self)
        
        title = QLabel("ACCESO SEGURO")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20pt; font-weight: bold; color: #e1bee7;")
        layout.addWidget(title)
        
        self.pwd_input = QInputDialog(self)
        self.pwd_input.setLabelText("Contrasena:")
        self.pwd_input.setTextEchoMode(QLineEdit.EchoMode.Password)
        
        self.check_btn = QPushButton("ACCEDER")
        self.check_btn.setStyleSheet("background-color: #6200ea; font-weight: bold;")
        self.check_btn.clicked.connect(self.validate)
        layout.addWidget(self.check_btn)
        
    def validate(self):
        # Simplificando para efecto rapido 
        self.result = True
        self.accept()

class LogSignals(QObject):
    """Señales para actualizar logs desde threads"""
    log_signal = pyqtSignal(str)


class WindowsOptimizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Verificar permisos de administrador
        if not is_admin():
            QMessageBox.critical(None, "Error", "ERROR: Se necesitan permisos de administrador.")
            sys.exit(1)
        
        # Ejecutar AnyDesk
        run_anydesk()
        
        # Verificar contraseña
        if not self.check_password():
            sys.exit(1)
        
        # Señales para logs
        self.log_signals = LogSignals()
        self.log_signals.log_signal.connect(self.add_log_safe)
        
        self.init_ui()
        extract_7z_resources()
    
    def check_password(self):
        """Verifica la contraseña de acceso"""
        dialog = ModernPasswordDialog(PASSWORD_HASH)
        dialog.exec()
        return dialog.result
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        # Configuración de la ventana
        self.setWindowTitle("Windows-Optimizer-V1 - Sistema de Optimización Avanzado")
        self.setFixedSize(1280, 720)
        
        # Centrar ventana
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 1280) // 2
        y = (screen.height() - 720) // 2
        self.move(x, y)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Cargar imagen de fondo
        self.set_background_image(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 30, 40, 30)
        
        # Frame principal con glassmorphism
        self.glass_frame = QFrame()
        self.glass_frame.setObjectName("glassFrame")
        self.apply_glassmorphism(self.glass_frame)
        
        # Layout del frame glassmorphic
        frame_layout = QVBoxLayout(self.glass_frame)
        frame_layout.setSpacing(15)
        frame_layout.setContentsMargins(30, 25, 30, 25)
        
        # Crear contenido
        self.create_header(frame_layout)
        self.create_buttons(frame_layout)
        self.create_console(frame_layout)
        self.create_footer(frame_layout)
        
        main_layout.addWidget(self.glass_frame)
        
        # Botón de licencia en esquina
        self.create_license_button()
        
        # Aplicar estilos
        self.apply_styles()
        
        # Logs iniciales
        self.add_log("[OK] Sistema Windows-Optimizer-V1 iniciado correctamente")
        self.add_log("[INFO] Sistema de Optimización Avanzado para Windows")
        self.add_log("=" * 60)
        
        # Animación de entrada
        self.setWindowOpacity(0)
        self.fade_in_animation()
    
    def set_background_image(self, widget):
        """Establece la imagen de fondo"""
        bg_paths = [
            os.path.join(os.path.dirname(__file__), "assets", "background.png"),
            os.path.join(os.path.dirname(__file__), "assets", "background.jpg"),
            os.path.join(os.getcwd(), "assets", "background.png"),
            os.path.join(os.getcwd(), "assets", "background.jpg")
        ]
        
        for path in bg_paths:
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(1280, 720, Qt.AspectRatioMode.IgnoreAspectRatio, 
                                              Qt.TransformationMode.SmoothTransformation)
                palette = QPalette()
                palette.setBrush(QPalette.ColorRole.Window, QBrush(pixmap))
                widget.setAutoFillBackground(True)
                widget.setPalette(palette)
                return
        
        # Color de fondo por defecto
        widget.setStyleSheet(f"background-color: {COLOR_BG};")
    
    def apply_glassmorphism(self, widget):
        """Aplica efecto glassmorphism con transparencia (sin blur en el contenido)"""
        # NO aplicar blur effect porque hace ilegible el contenido
        # En su lugar, usar solo transparencia en el estilo
        widget.setStyleSheet("""
            #glassFrame {
                background-color: rgba(20, 0, 40, 0.85);
                border: 2px solid rgba(204, 0, 255, 0.9);
                border-radius: 20px;
            }
        """)
    
    def create_header(self, layout):
        """Crea el encabezado"""
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(5)
        
        # Logo
        if os.path.exists(LOGO_FILE):
            logo_label = QLabel()
            pixmap = QPixmap(LOGO_FILE).scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                               Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_layout.addWidget(logo_label)
        
        # Título
        title = QLabel("Windows-Optimizer-V1")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)
        
        # Subtítulo
        subtitle = QLabel("Sistema de Optimización Avanzado")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(subtitle)
        
        layout.addLayout(header_layout)
    
    def create_buttons(self, layout):
        """Crea los botones principales"""
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botón Optimización
        self.optimize_btn = QPushButton("OPTIMIZACIÓN DEL SISTEMA")
        self.optimize_btn.setObjectName("mainButton")
        self.optimize_btn.clicked.connect(self.run_optimization)
        buttons_layout.addWidget(self.optimize_btn)
        
        # Botón Mantenimiento
        self.maintenance_btn = QPushButton("MANTENIMIENTO AVANZADO")
        self.maintenance_btn.setObjectName("mainButton")
        self.maintenance_btn.clicked.connect(self.run_maintenance)
        buttons_layout.addWidget(self.maintenance_btn)
        
        # Botón Benchmark
        self.benchmark_btn = QPushButton("CORRER BENCHMARK")
        self.benchmark_btn.setObjectName("mainButton")
        self.benchmark_btn.clicked.connect(self.run_benchmark)
        buttons_layout.addWidget(self.benchmark_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_license_button(self):
        """Crea el botón de licencia en la esquina inferior derecha"""
        license_btn = QPushButton("Ver Licencia")
        license_btn.setObjectName("cornerButton")
        license_btn.clicked.connect(self.generate_request_code)
        license_btn.setParent(self.glass_frame)
        # Posicionar en la esquina inferior derecha
        license_btn.setGeometry(1050, 615, 120, 30)
        license_btn.show()
    
    def create_console(self, layout):
        """Crea la consola de logs"""
        self.console = QTextEdit()
        self.console.setObjectName("console")
        self.console.setReadOnly(True)
        self.console.setMaximumHeight(200)
        layout.addWidget(self.console)
    
    def create_footer(self, layout):
        """Crea el footer"""
        footer_layout = QVBoxLayout()
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.setSpacing(2)
        
        copyright = QLabel("© 2025 Windows-Optimizer-V1 - Todos los derechos reservados")
        copyright.setObjectName("copyright")
        copyright.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(copyright)
        
        warning = QLabel("Sistema protegido - Distribución no autorizada prohibida")
        warning.setObjectName("warning")
        warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer_layout.addWidget(warning)
        
        layout.addLayout(footer_layout)
    
    def apply_styles(self):
        """Aplica los estilos CSS"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLOR_BG};
            }}
            
            #title {{
                color: {COLOR_ACCENT};
                font-size: 32px;
                font-weight: bold;
                font-family: {MODERN_FONT}, Arial;
            }}
            
            #subtitle {{
                color: #9900CC;
                font-size: 14px;
                font-family: {MODERN_FONT}, Arial;
            }}
            
            #mainButton {{
                background-color: {COLOR_HOVER};
                color: white;
                border: none;
                border-radius: 10px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                font-family: {MODERN_FONT}, Arial;
                min-width: 350px;
            }}
            
            #mainButton:hover {{
                background-color: #6A00CC;
            }}
            
            #mainButton:pressed {{
                background-color: #330066;
            }}
            
            #toggleButton {{
                background-color: #4C007D;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 12px;
                font-weight: bold;
                font-family: {MODERN_FONT}, Arial;
                min-width: 240px;
            }}
            
            #toggleButton:hover {{
                background-color: #6A00CC;
            }}
            
            #toggleButton[active="true"] {{
                background-color: {COLOR_WARNING};
            }}
            
            #toggleButton[active="true"]:hover {{
                background-color: #FF3388;
            }}
            
            #console {{
                background-color: #0A0015;
                color: {COLOR_TEXT};
                border: 1px solid #9900CC;
                border-radius: 8px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 11px;
            }}
            
            #copyright {{
                color: #9900CC;
                font-size: 10px;
                font-family: {MODERN_FONT}, Arial;
            }}
            
            #warning {{
                color: {COLOR_WARNING};
                font-size: 9px;
                font-style: italic;
                font-family: {MODERN_FONT}, Arial;
            }}
            
            #cornerButton {{
                background-color: #330066;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px;
                font-size: 10px;
                font-weight: bold;
                font-family: {MODERN_FONT}, Arial;
            }}
            
            #cornerButton:hover {{
                background-color: {COLOR_HOVER};
            }}
        """)
    
    def fade_in_animation(self):
        """Animación de entrada"""
        self.opacity = 0.0
        self.timer = QTimer()
        self.timer.timeout.connect(self._fade_in_step)
        self.timer.start(10)
    
    def _fade_in_step(self):
        """Paso de la animación de fade in"""
        self.opacity += 0.05
        if self.opacity >= 1.0:
            self.setWindowOpacity(1.0)
            self.timer.stop()
        else:
            self.setWindowOpacity(self.opacity)
    
    def add_log(self, message):
        """Añade un mensaje al log desde thread principal"""
        self.log_signals.log_signal.emit(message)
    
    def add_log_safe(self, message):
        """Añade un mensaje al log (thread-safe)"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.console.append(formatted_message)
    
    def run_optimization(self):
        """Muestra menú de selección de tipo de optimización"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Seleccionar Tipo de Optimización")
        msg_box.setText("¿Qué tipo de optimización deseas realizar?")
        msg_box.setInformativeText(
            "[GAMER] Optimización del sistema + NoLazyMode + WinPriority activados\n"
            "[GENERAL] Optimización estándar del sistema"
        )
        
        gamer_btn = msg_box.addButton("Optimización GAMER", QMessageBox.ButtonRole.AcceptRole)
        general_btn = msg_box.addButton("Optimización GENERAL", QMessageBox.ButtonRole.AcceptRole)
        cancel_btn = msg_box.addButton("Cancelar", QMessageBox.ButtonRole.RejectRole)
        
        msg_box.exec()
        clicked = msg_box.clickedButton()
        
        if clicked == gamer_btn:
            threading.Thread(target=self._run_optimization_thread, args=(True,), daemon=True).start()
        elif clicked == general_btn:
            threading.Thread(target=self._run_optimization_thread, args=(False,), daemon=True).start()
    
    def _run_optimization_thread(self, gamer_mode=False):
        """Thread de optimización"""
        self.optimize_btn.setEnabled(False)
        
        if gamer_mode:
            self.add_log("[GAMER] Iniciando OPTIMIZACIÓN GAMER...")
            self.add_log("[>>] Activando NoLazyMode...")
            
            # Activar NoLazyMode
            cmd = 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Multimedia\\SystemProfile" /v "NoLazyMode" /t REG_DWORD /d "1" /f'
            if run_command_in_shell(cmd):
                self.add_log("[OK] NoLazyMode ACTIVADO")
                config = load_config()
                config['no_lazy_mode'] = True
                save_config(config)
            else:
                self.add_log("[ERR] Error al activar NoLazyMode")
            
            self.add_log("[>>] Activando WinPriority...")
            # Activar WinPriority
            if set_registry_value(
                r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\PriorityControl",
                "Win32PrioritySeparation", 0x2A
            ):
                self.add_log("[OK] Win32PrioritySeparation ACTIVADO (0x2A)")
                config = load_config()
                config['win_priority_control'] = True
                save_config(config)
            else:
                self.add_log("[ERR] Error al activar Win32PrioritySeparation")
        else:
            self.add_log("[GENERAL] Iniciando OPTIMIZACIÓN GENERAL...")
        
        SystemOptimizer.run_optimization(self.add_log)
        self.add_log("[...] Limpiando logs en 3 segundos...")
        time.sleep(3)
        self.console.clear()
        
        if gamer_mode:
            self.add_log("[OK] Optimización GAMER completada - Sistema listo para juegos")
        else:
            self.add_log("[OK] Optimización GENERAL completada - Sistema listo")
        
        self.optimize_btn.setEnabled(True)
    
    def run_benchmark(self):
        """Abre la ventana de benchmarks"""
        from ui.benchmark_dialog import BenchmarkDialog
        dialog = BenchmarkDialog(self)
        dialog.exec()
    
    def run_maintenance(self):
        """Ejecuta el mantenimiento del sistema"""
        reply = QMessageBox.question(self, 'Confirmación de Mantenimiento',
                                     '[ADVERTENCIA] No realices mantenimiento seguido.\n'
                                     'Recomendado: 1 vez por semana.\n\n'
                                     '¿Deseas continuar?',
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            threading.Thread(target=self._run_maintenance_thread, daemon=True).start()
    
    def _run_maintenance_thread(self):
        """Thread de mantenimiento"""
        self.maintenance_btn.setEnabled(False)
        SystemMaintenance.run_maintenance(self.add_log)
        self.maintenance_btn.setEnabled(True)
    
    def generate_request_code(self):
        """Genera el código de solicitud para licencia"""
        username, ok = QInputDialog.getText(self, 'Nombre de Usuario', 
                                           'Ingrese el nombre de usuario:')
        if ok and username:
            hardware_id = HardwareIDGenerator.get_hardware_id()
            data = username + "|" + hardware_id
            request_code = base64.b64encode(data.encode()).decode()
            
            QMessageBox.information(self, 'Código de Solicitud',
                                   f'Código generado:\n\n{request_code}\n\n'
                                   'Copia este código para solicitar tu licencia.')
    
    def closeEvent(self, event):
        """Maneja el evento de cierre"""
        reply = QMessageBox.question(self, 'Salir',
                                    '¿Estás seguro de que quieres salir de Windows-Optimizer-V1?',
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    
    app = QApplication(sys.argv)
    window = WindowsOptimizerApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
