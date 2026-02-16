# Windows-Optimizer-V1

![Windows Optimizer](https://img.shields.io/badge/Platform-Windows-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)
![License](https://img.shields.io/badge/License-Proprietary-red)

**Windows-Optimizer-V1** es un sistema de optimización avanzado para Windows que permite mejorar el rendimiento del sistema mediante ajustes de registro, limpieza de archivos temporales, y optimizaciones del sistema.

## 🚀 Características

- ⚡ **Optimización del Sistema**: Mejora el rendimiento de Windows con ajustes automáticos
- 🔧 **Mantenimiento Avanzado**: Limpieza profunda del sistema
- 🎛️ **Control de Prioridades**: Ajustes de Win32PrioritySeparation y NoLazyMode
- 🔑 **Sistema de Licencias**: Generación de claves de licencia basadas en hardware
- 🎨 **Interfaz Moderna**: Diseño profesional con Tkinter

## 📋 Requisitos

- Windows 10/11 (22H2 o superior)
- Python 3.8 o superior
- Permisos de Administrador

## 📦 Dependencias

```bash
pip install pillow
```

## 🖼️ Configurar Imagen de Fondo

Para personalizar la imagen de fondo de la aplicación:

1. **Coloca tu imagen** en la carpeta `assets/` del proyecto:
   ```
   Windows-Optimizer-V1/
   └── assets/
       └── background.png
   ```

2. **Formatos soportados**: PNG o JPG
3. **Tamaño recomendado**: 900x700 píxeles
4. **Nombre del archivo**: `background.png` o `background.jpg`

> **Nota**: Si no se encuentra ninguna imagen, el programa usará un fondo de color sólido por defecto.

## 🎯 Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/augustolu/Windows-Optimizer-V1.git
   cd Windows-Optimizer-V1
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. (Opcional) Coloca tu imagen de fondo en la carpeta `assets/`

4. Ejecuta el programa **como Administrador**:
   ```bash
   python cache_core.py
   ```

## 🔐 Uso

1. **Ejecutar como Administrador**: El programa requiere permisos de administrador para funcionar correctamente
2. **Contraseña**: Ingresa la contraseña al iniciar (configurada en el sistema)
3. **Optimización**: Haz clic en "⚡ OPTIMIZACIÓN DEL SISTEMA" para mejorar el rendimiento
4. **Mantenimiento**: Usa "🔧 MANTENIMIENTO AVANZADO" para limpiar archivos temporales (recomendado 1 vez por semana)

## 🛠️ Características Técnicas

### Optimizaciones Disponibles

- **NoLazyMode**: Optimización de la gestión de procesos en Windows
- **Win32PrioritySeparation**: Control de la separación de prioridades del sistema
- **Limpieza de Caché**: Elimina archivos temporales y cachés del sistema
- **Optimización de DNS**: Limpia la caché DNS para mejorar la conectividad

### Estructura del Proyecto

```
Windows-Optimizer-V1/
├── assets/              # Carpeta para imagen de fondo
├── config/              # Configuraciones del sistema
├── features/            # Módulos de optimización y mantenimiento
├── ui/                  # Componentes de interfaz de usuario
├── utils/               # Utilidades del sistema
├── cache_core.py        # Punto de entrada principal
├── main.py              # Aplicación principal
└── README.md            # Este archivo
```

## ⚠️ Advertencias

- **Requiere permisos de Administrador**: El programa modifica configuraciones del sistema
- **Uso responsable**: No ejecutar mantenimiento con demasiada frecuencia (máximo 1 vez por semana)
- **Respaldo**: Se recomienda crear un punto de restauración antes de usar

## 📄 Licencia

© 2025 Windows-Optimizer-V1 - Todos los derechos reservados. Sistema protegido por leyes de propiedad intelectual.

---

**Nota**: Este software está protegido. Distribución no autorizada prohibida.
