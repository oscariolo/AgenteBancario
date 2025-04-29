import pygame
import random
import sys
from collections import deque

# Inicializar Pygame
pygame.init()
# Inicializar fuente
font = pygame.font.SysFont("Arial", 20)  # Added font initialization

# Tamaño de pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulación Agencia Bancaria")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (100, 200, 100)
RED = (200, 100, 100)
BLUE = (100, 100, 250)
YELLOW = (250, 250, 100)

# Configuración
FPS = 60
clock = pygame.time.Clock()

# Configuración de ventanillas
NUM_VENTANILLAS = 3
ventanillas = [{'ocupado': False, 'cliente': None, 'tiempo_restante': 0} for _ in range(NUM_VENTANILLAS)]

# Cliente
class Cliente:
    def __init__(self, id, especial):
        self.id = id
        self.especial = especial  # True if priority attention is needed
        # Priority clients will be blue, the rest yellow.
        self.color = BLUE if especial else YELLOW
        self.priority = "High" if especial else "Normal"  # added priority tag

# Configuración de clientes
cliente_id = 0
fila = deque()
# Add 4 common clients to start the queue
for _ in range(4):
    fila.append(Cliente(cliente_id, False))
    cliente_id += 1



# Función para generar clientes aleatorios
def generar_cliente():
    global cliente_id
    especial = random.random() < 0.2  # 20% de probabilidad de atención especial
    cliente = Cliente(cliente_id, especial)
    cliente_id += 1
    fila.append(cliente)

def dibujar_ventanillas():
    cell_width = 100
    cell_height = 100
    margin = 20
    for idx, v in enumerate(ventanillas):
        x = 100 + idx * (cell_width + margin)
        y = 50
        # Ventanilla base
        color = RED if v['ocupado'] else GREEN
        pygame.draw.rect(screen, color, (x, y, cell_width, cell_height))
        # Si la ventanilla está atendiendo a un cliente, dibujar su cuadrado
        if v['ocupado'] and v['cliente']:
            # Dibujar cuadrado (tamaño menor) centrado en la ventanilla
            square_size = 20
            square_x = x + (cell_width - square_size) // 2
            square_y = y + (cell_height - square_size) // 2
            pygame.draw.rect(screen, v['cliente'].color, (square_x, square_y, square_size, square_size))
            # Renderizar el id del cliente (opcional, en centro de cuadrado)
            text = font.render(str(v['cliente'].id), True, BLACK)
            text_rect = text.get_rect(center=(square_x + square_size//2, square_y + square_size//2))
            screen.blit(text, text_rect)

def dibujar_fila():
    # Dibuja la fila de clientes como columna centrada debajo de ventanillas
    square_size = 20
    spacing = 5
    # Calcular posición x centrada
    x = WIDTH // 2 - square_size // 2
    # Posición y inicia justo debajo de las ventanillas (y + cell_height + margin)
    start_y = 50 + 100 + 20
    y = start_y
    for cliente in fila:
        pygame.draw.rect(screen, cliente.color, (x, y, square_size, square_size))
        # Renderizar el id del cliente (opcional, en centro de cuadrado)
        text = font.render(str(cliente.id), True, BLACK)
        text_rect = text.get_rect(center=(x + square_size//2, y + square_size//2))
        screen.blit(text, text_rect)
        y += square_size + spacing

# Lógica del agente inteligente
def asignar_cliente_a_ventanilla():
    # Buscar ventanillas libres
    libres = [i for i, v in enumerate(ventanillas) if not v['ocupado']]
    if not libres:
        return

    for i in libres:
        if not fila:  # Verificar si no hay clientes en espera
            break
        # Recalcular el índice del cliente especial en cada iteración
        especial_idx = next((idx for idx, c in enumerate(fila) if c.especial), None)
        if especial_idx is not None:
            cliente = fila[especial_idx]
            del fila[especial_idx]
        else:
            cliente = fila.popleft()

        ventanillas[i]['ocupado'] = True
        ventanillas[i]['cliente'] = cliente
        ventanillas[i]['tiempo_restante'] = random.randint(3, 7) * FPS  # Tiempo aleatorio entre 3-7 segundos

# Actualizar ventanillas
def actualizar_ventanillas():
    for v in ventanillas:
        if v['ocupado']:
            v['tiempo_restante'] -= 1
            if v['tiempo_restante'] <= 0:
                v['ocupado'] = False
                v['cliente'] = None

# Main loop
def main():
    spawn_timer = 0
    assignment_timer = random.randint(FPS, FPS * 3)  # random delay for attending (1-3 seconds)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(WHITE)
        spawn_timer += 1
        assignment_timer -= 1

        if spawn_timer > FPS * 1:  # New client every 1 second
            generar_cliente()
            spawn_timer = 0

        if assignment_timer <= 0:
            asignar_cliente_a_ventanilla()
            assignment_timer = random.randint(FPS, FPS * 3)  # reset assignment delay

        actualizar_ventanillas()
        dibujar_fila()
        dibujar_ventanillas()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
