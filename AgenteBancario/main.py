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
NUM_VENTANILLAS = 5
ventanillas = [{'ocupado': False, 'cliente': None, 'tiempo_restante': 0} for _ in range(NUM_VENTANILLAS)]
# Dimensiones de clientes
CLIENT_SIZE = 40

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

paused = False  # Variable global para pausar el tiempo

def manejar_eventos():
    global paused
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:  # Pausar/reanudar con la tecla P
                paused = not paused
                
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
    square_size = CLIENT_SIZE
    total_width = NUM_VENTANILLAS * cell_width + (NUM_VENTANILLAS - 1) * margin
    offset_x = (WIDTH - total_width) // 2
    for idx, v in enumerate(ventanillas):
        x = offset_x + idx * (cell_width + margin)
        y = 50  # Asegúrate de que esto no interfiera con el panel inferior
        color = RED if v['ocupado'] else GREEN
        pygame.draw.rect(screen, color, (x, y, cell_width, cell_height))
        if v['ocupado'] and v['cliente']:
            if v.get('animating', False):
                sp = v['start_pos']
                tp = v['target_pos']
                progress = v['anim_progress']
                square_x = sp[0] + (tp[0] - sp[0]) * progress
                square_y = sp[1] + (tp[1] - sp[1]) * progress
            else:
                square_x = x + (cell_width - square_size) // 2
                square_y = y + (cell_height - square_size) // 2
            pygame.draw.rect(screen, v['cliente'].color, (square_x, square_y, square_size, square_size))
            text = font.render(str(v['cliente'].id), True, BLACK)
            text_rect = text.get_rect(center=(square_x + square_size // 2, square_y + square_size // 2))
            screen.blit(text, text_rect)

def dibujar_pantalla_turnos():
    try:
        # Dimensiones del panel
        panel_width = 200
        panel_height = NUM_VENTANILLAS * 30 + 20
        # Coordenadas para la parte inferior izquierda
        panel_x = 10  # Margen izquierdo
        panel_y = HEIGHT - panel_height - 10  # Margen inferior
        
        # Dibujar el rectángulo del panel
        pygame.draw.rect(screen, (255, 200, 200), (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

        # Dibujar el texto de los turnos dentro del panel
        text_y = panel_y + 10
        for idx, v in enumerate(ventanillas):
            turno_text = f"Ventanilla {idx + 1}: "
            if v['ocupado'] and v['cliente']:
                turno_text += f"Cliente {v['cliente'].id}"
            else:
                turno_text += "Libre"
            text = font.render(turno_text, True, BLACK)
            screen.blit(text, (panel_x + 10, text_y))
            text_y += 30
    except Exception as e:
        print("Error al dibujar la pantalla de turnos:", e)

def dibujar_fila():
    # Dibuja la fila de clientes como columna centrada debajo de ventanillas
    square_size = CLIENT_SIZE
    spacing = 10
    # Compute total height for the queued clients to center vertically
    total_height = len(fila) * square_size + (len(fila) - 1) * spacing if fila else 0
    y = (HEIGHT - total_height) // 2 if total_height else 50 + 100 + 20
    # Calcular posición x centrada
    x = WIDTH // 2 - square_size // 2
    for cliente in fila:
        pygame.draw.rect(screen, cliente.color, (x, y, square_size, square_size))
        text = font.render(str(cliente.id), True, BLACK)
        text_rect = text.get_rect(center=(x + square_size // 2, y + square_size // 2))
        screen.blit(text, text_rect)
        y += square_size + spacing
        
def dibujar_mensaje_pausa():
    if paused:
        mensaje = "Simulación en PAUSA. Presiona 'P' para continuar."
        text = font.render(mensaje, True, RED)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        screen.blit(text, text_rect)

# Lógica del agente inteligente
def asignar_cliente_a_ventanilla():
    # Buscar ventanillas libres
    libres = [i for i, v in enumerate(ventanillas) if not v['ocupado']]
    if not libres:
        return

    for i in libres:
        if not fila:
            break
        # Pick special client if exists; capture its queue index
        especial_idx = next((idx for idx, c in enumerate(fila) if c.especial), None)
        if especial_idx is not None:
            cliente = fila[especial_idx]
            queue_index = especial_idx
            # Compute animation's start using the current queue drawing logic
            square_size = CLIENT_SIZE
            spacing = 5
            count = len(fila) + 1  # include the client being assigned
            total_height = count * square_size + (count - 1) * spacing
            start_y = (HEIGHT - total_height) // 2  # match dibujar_fila's vertical centering
            start_pos = (WIDTH // 2 - square_size // 2, start_y + queue_index * (square_size + spacing))
            del fila[especial_idx]
        else:
            queue_index = 0
            # Compute animation's start using the current queue drawing logic
            square_size = CLIENT_SIZE
            spacing = 5
            count = len(fila) + 1  # include the client being assigned
            total_height = count * square_size + (count - 1) * spacing
            start_y = (HEIGHT - total_height) // 2  # match dibujar_fila's vertical centering
            start_pos = (WIDTH // 2 - square_size // 2, start_y + queue_index * (square_size + spacing))
            cliente = fila[0]
            fila.popleft()
        
        cell_width = 100
        cell_height = 100
        margin = 20
        total_width = NUM_VENTANILLAS * cell_width + (NUM_VENTANILLAS - 1) * margin
        offset_x = (WIDTH - total_width) // 2
        x_cell = offset_x + i * (cell_width + margin)
        y_cell = 50
        target_pos = (x_cell + (cell_width - square_size) // 2, y_cell + (cell_height - square_size) // 2)
        
        service_time = random.randint(5, 10) * FPS
        ventanillas[i] = {
            'ocupado': True,
            'cliente': cliente,
            'tiempo_restante': service_time,
            'animating': True,
            'anim_progress': 0.0,
            'start_pos': start_pos,
            'target_pos': target_pos
        }

# Actualizar ventanillas
def actualizar_ventanillas():
    for v in ventanillas:
        if v['ocupado']:
            # Update animation progress first if animation is active
            if v.get('animating', False):
                v['anim_progress'] += 1 / (1.5 * FPS)
                if v['anim_progress'] >= 1:
                    v['anim_progress'] = 1
                    v['animating'] = False
            else:
                v['tiempo_restante'] -= 1
                if v['tiempo_restante'] <= 0:
                    v['ocupado'] = False
                    v['cliente'] = None
                    # Clear any animation fields
                    v.pop('animating', None)
                    v.pop('anim_progress', None)
                    v.pop('start_pos', None)
                    v.pop('target_pos', None)

# Main loop
def main():
    spawn_timer = 0
    assignment_timer = random.randint(FPS * 3, FPS * 5)
    while True:
        manejar_eventos()  # Manejar eventos (incluida la pausa)

        if not paused:  # Solo actualizar si no está en pausa
            screen.fill(WHITE)
            spawn_timer += 1
            assignment_timer -= 1

            if spawn_timer > FPS * 2:  # Nuevo cliente cada 2 segundos
                generar_cliente()
                spawn_timer = 0

            if assignment_timer <= 0:
                asignar_cliente_a_ventanilla()
                assignment_timer = random.randint(FPS, FPS * 3)

            actualizar_ventanillas()
            
        # Dibujo de elementos
        dibujar_fila()
        dibujar_ventanillas()
        dibujar_pantalla_turnos()  # Dibujar la pantalla de turnos en la parte inferior izquierda
        dibujar_mensaje_pausa()  # Dibujar el mensaje de pausa si está pausado

        pygame.display.flip()
        clock.tick(FPS)
        
if __name__ == "__main__":
    main()
