import pygame
import socket
import os

# Configuração do protocolo de transporte UDP
IP_DO_PC = "xxx.xxx.xx.xx" 
PORTA = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Driver 'android' evita tentativa de abertura de janela desktop no Pydroid 3
os.environ['SDL_VIDEODRIVER'] = 'android'
pygame.init()
screen = pygame.display.set_mode((600, 900))
pygame.joystick.init()

def buscar_controle():
    if pygame.joystick.get_count() > 0:
        joy = pygame.joystick.Joystick(0)
        joy.init()
        return joy
    return None

js = buscar_controle()
last_state = {}

def enviar(chave, valor):
    global last_state
    # Envio diferencial: transmite apenas mudanças de estado para otimizar a rede
    if last_state.get(chave) != valor:
        msg = f"{chave}:{valor}"
        try:
            sock.sendto(msg.encode(), (IP_DO_PC, PORTA))
            last_state[chave] = valor
        except Exception as e:
            print(f"Erro de rede: {e}")

print("Iniciando transmissão direta...")

while True:
    # Processa a fila de eventos do sistema para manter a aplicação responsiva
    pygame.event.pump()
    
    if js:
        # 1. Processamento de Eixos (Analógicos e Gatilhos)
        for i in range(js.get_numaxes()):
            val = round(js.get_axis(i), 2)
            # Deadzone básica para ignorar ruídos próximos ao centro (drift)
            if abs(val) < 0.05: val = 0.0
            enviar(f"Eixo_{i}", val)

        # 2. Processamento de Botões Digitais
        for i in range(js.get_numbuttons()):
            enviar(f"Botao_{i}", js.get_button(i))

        # 3. Processamento de Hats (D-Pad)
        for i in range(js.get_numhats()):
            hat = js.get_hat(i)
            enviar(f"Hat_{i}_X", hat[0])
            enviar(f"Hat_{i}_Y", hat[1])
            
    else:
        js = buscar_controle()

    # Atualização de tela necessária para evitar suspensão do processo pelo Android
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
    # Limitação da taxa de amostragem para 60Hz
    pygame.time.Clock().tick(60)