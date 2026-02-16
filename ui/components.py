import tkinter as tk
import time
from config.settings import COLOR_HOVER, COLOR_WARNING, MULTI_LINE_FONT, MODERN_FONT, COLOR_ACCENT

class RoundedButton(tk.Canvas):
    """Botón personalizado con bordes redondeados, gradientes y animaciones"""
    def __init__(self, parent, width=120, height=40, corner_radius=10, 
                 bg_color=COLOR_HOVER, hover_color="#6A00CC", active_color=COLOR_WARNING,
                 text="Button", text_color="#FFFFFF", font=(MODERN_FONT, 12, "bold"), 
                 command=None, is_active=False):
        super().__init__(parent, width=width, height=height, 
                        highlightthickness=0, bg=parent.cget("bg"))
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.corner_radius = corner_radius
        self.text = text
        self.text_color = text_color
        self.font = font
        self.is_active = is_active
        self.transition_alpha = 0.0
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
        self.draw_button()
    
    def draw_button(self, color=None):
        """Dibuja el botón con bordes redondeados, sombra y gradiente"""
        self.delete("all")
        
        if color is None:
            color = self.active_color if self.is_active else self.bg_color
        
        # Crear sombra
        self.create_rounded_rect(2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2, 
                               self.corner_radius, fill="#20003A", outline="")
        
        # Crear botón con gradiente
        self.create_gradient_rect(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                                color, "#330066")
        
        # Texto con sombra
        self.create_text(self.winfo_reqwidth()/2 + 1, self.winfo_reqheight()/2 + 1,
                        text=self.text, fill="#000000", font=self.font)
        self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2,
                        text=self.text, fill=self.text_color, font=self.font)
    
    def create_rounded_rect(self, x1, y1, x2, y2, r=10, **kwargs):
        """Crea un rectángulo con bordes redondeados"""
        points = [x1+r, y1,
                 x2-r, y1,
                 x2, y1,
                 x2, y1+r,
                 x2, y2-r,
                 x2, y2,
                 x2-r, y2,
                 x1+r, y2,
                 x1, y2,
                 x1, y2-r,
                 x1, y1+r,
                 x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)
    
    def create_gradient_rect(self, x1, y1, x2, y2, color1, color2):
        """Crea un rectángulo con gradiente"""
        steps = 50
        for i in range(steps):
            ratio = i / steps
            r1, g1, b1 = self.winfo_rgb(color1)
            r2, g2, b2 = self.winfo_rgb(color2)
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = f"#{r>>8:02x}{g>>8:02x}{b>>8:02x}"
            y_start = y1 + (y2 - y1) * (i / steps)
            y_end = y1 + (y2 - y1) * ((i + 1) / steps)
            self.create_rounded_rect(x1, y_start, x2, y_end, self.corner_radius, 
                                   fill=color, outline="")
    
    def on_enter(self, event):
        """Cuando el mouse entra en el botón"""
        self.create_glow_effect()
        if self.is_active:
            self.draw_button("#FF3388")
        else:
            self.animate_color_transition(self.bg_color, self.hover_color)
    
    def on_leave(self, event):
        """Cuando el mouse sale del botón"""
        if self.is_active:
            self.draw_button(self.active_color)
        else:
            self.animate_color_transition(self.hover_color, self.bg_color)
    
    def create_glow_effect(self):
        """Crea un efecto de brillo al pasar el mouse"""
        self.create_rounded_rect(-2, -2, self.winfo_reqwidth()+2, self.winfo_reqheight()+2,
                               self.corner_radius+2, outline=COLOR_ACCENT, width=2)
    
    def animate_color_transition(self, start_color, end_color):
        """Anima una transición de color suave"""
        def interpolate_color(start, end, factor):
            r1, g1, b1 = self.winfo_rgb(start_color)
            r2, g2, b2 = self.winfo_rgb(end_color)
            r = int(r1 + (r2 - r1) * factor)
            g = int(g1 + (g2 - g1) * factor)
            b = int(b1 + (b2 - b1) * factor)
            return f"#{r>>8:02x}{g>>8:02x}{b>>8:02x}"
        
        def transition(step=0):
            if step <= 10:
                factor = step / 10
                color = interpolate_color(start_color, end_color, factor)
                self.draw_button(color)
                self.after(20, transition, step + 1)
        
        transition()
    
    def on_click(self, event):
        """Cuando se hace clic en el botón"""
        self.scale_button(0.95)
        self.after(100, self.scale_button, 1.0)
        if self.command:
            self.command()
    
    def scale_button(self, scale):
        """Escala el botón para un efecto de clic"""
        self.delete("all")
        width = self.winfo_reqwidth() * scale
        height = self.winfo_reqheight() * scale
        x_offset = (self.winfo_reqwidth() - width) / 2
        y_offset = (self.winfo_reqheight() - height) / 2
        
        color = self.active_color if self.is_active else self.bg_color
        self.create_rounded_rect(x_offset, y_offset, x_offset + width, y_offset + height, 
                               self.corner_radius, fill=color, outline="")
        self.create_text(self.winfo_reqwidth()/2, self.winfo_reqheight()/2,
                        text=self.text, fill=self.text_color, font=self.font)
    
    def set_active(self, active):
        """Cambia el estado activo/inactivo del botón"""
        self.is_active = active
        if active:
            self.draw_button(self.active_color)
        else:
            self.draw_button(self.bg_color)
    
    def update_text(self, new_text):
        """Actualiza el texto del botón"""
        self.text = new_text
        self.draw_button()

class ConsoleManager:
    """Gestor de consola para mostrar logs de manera eficiente"""
    def __init__(self, text_widget, max_lines=100):
        self.text_widget = text_widget
        self.max_lines = max_lines
        self.lines = []
        
    def add_log(self, message):
        """Añade un mensaje al log"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.lines.append(formatted_message)
        
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]
        
        self.update_display()
    
    def update_display(self):
        """Actualiza la visualización de la consola"""
        self.text_widget.config(state="normal")
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.insert(tk.END, "\n".join(self.lines))
        self.text_widget.see(tk.END)
        self.text_widget.config(state="disabled")
    
    def clear(self):
        """Limpia la consola"""
        self.lines.clear()
        self.text_widget.config(state="normal")
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state="disabled")
