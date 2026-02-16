import math
import random
from config.settings import COLOR_ACCENT

class NeuralNetworkAnimation:
    """Animación de fondo con redes neuronales conectándose - Versión mejorada"""
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.nodes = []
        self.connections = []
        self.node_radius = 4
        self.speed = 1.5
        self.pulse_value = 0
        self.pulse_direction = 1
        self.setup_animation()
        
    def setup_animation(self):
        """Configura la animación inicial"""
        num_nodes = 50
        for _ in range(num_nodes):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            dx = random.uniform(-self.speed, self.speed)
            dy = random.uniform(-self.speed, self.speed)
            self.nodes.append({"x": x, "y": y, "dx": dx, "dy": dy})
        
        self.update_connections()
    
    def update_connections(self):
        """Actualiza las conexiones entre nodos"""
        self.connections = []
        for i, node1 in enumerate(self.nodes):
            for j, node2 in enumerate(self.nodes[i+1:], i+1):
                dx = node1["x"] - node2["x"]
                dy = node1["y"] - node2["y"]
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < 200:
                    strength = 1.0 - (distance / 200.0)
                    self.connections.append({
                        "node1": i, 
                        "node2": j, 
                        "strength": strength,
                        "distance": distance
                    })
    
    def update(self):
        """Actualiza la animación"""
        self.canvas.delete("neural")
        
        self.pulse_value += 0.05 * self.pulse_direction
        if self.pulse_value >= 1.0:
            self.pulse_value = 1.0
            self.pulse_direction = -1
        elif self.pulse_value <= 0.0:
            self.pulse_value = 0.0
            self.pulse_direction = 1
        
        for node in self.nodes:
            node["x"] += node["dx"]
            node["y"] += node["dy"]
            
            if node["x"] <= 0 or node["x"] >= self.width:
                node["dx"] *= -1
            if node["y"] <= 0 or node["y"] >= self.height:
                node["dy"] *= -1
                
            pulse_size = self.node_radius * (1 + 0.5 * self.pulse_value)
            self.canvas.create_oval(
                node["x"] - pulse_size, node["y"] - pulse_size,
                node["x"] + pulse_size, node["y"] + pulse_size,
                fill=COLOR_ACCENT, outline="", tags="neural"
            )
        
        self.update_connections()
        
        for conn in self.connections:
            node1 = self.nodes[conn["node1"]]
            node2 = self.nodes[conn["node2"]]
            
            intensity = int(150 + 105 * conn["strength"] * (0.7 + 0.3 * self.pulse_value))
            if intensity > 200:
                color = "#FF00FF"
            elif intensity > 170:
                color = "#FF33CC"
            elif intensity > 150:
                color = COLOR_ACCENT
            elif intensity > 130:
                color = "#9900FF"
            else:
                color = "#6600CC"
            
            line_width = max(1.5, conn["strength"] * 3)
            
            self.canvas.create_line(
                node1["x"], node1["y"], 
                node2["x"], node2["y"],
                fill=color, width=line_width, 
                tags="neural"
            )
        
        self.canvas.after(25, self.update)
