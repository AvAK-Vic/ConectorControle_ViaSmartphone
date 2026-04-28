import pygame
import socket
import os

# Configurações de rede UDP utilizadas para enviar eventos ao PC.
# IP_DO_PC deve apontar para o endereço local do receptor no Windows.
# PORTA deve ser a mesma porta que o receptor está escutando.

IP_DO_PC = "xxx.xxx.xx.xx" # Alterar pelo IP de seu PC
PORTA = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Inicialização do ambiente SDL no Android.
# O driver `android` é necessário para evitar que o Pygame tente abrir uma janela desktop.
os.environ['SDL_VIDEODRIVER'] = 'android'
pygame.init()
screen = pygame.display.set_mode((600, 900))
pygame.joystick.init()

def buscar_controle():
    """Procura um joystick conectado e inicializa a primeira unidade disponível.

    O Pygame mantém o conjunto de joysticks detectados em `pygame.joystick`.
    Essa função retorna o primeiro joystick conectado ou None quando nenhum estiver disponível.
    """
    if pygame.joystick.get_count() > 0:
        joy = pygame.joystick.Joystick(0)
        joy.init()
        return joy
    return None

js = buscar_controle()
last_state = {}

def enviar(chave, valor):
    global last_state
    # Debounce de rede: envia apenas quando o estado muda para reduzir pacotes UDP.
    # Isso evita tráfego desnecessário quando o joystick mantém uma posição constante.
    if last_state.get(chave) != valor:
        msg = f"{chave}:{valor}"
        sock.sendto(msg.encode(), (IP_DO_PC, PORTA))
        last_state[chave] = valor

print("Iniciando transmissão direta...")

while True:
    pygame.event.pump()
    
    if js:
        # 1. Eixos analógicos e gatilhos são lidos como valores contínuos entre -1.0 e 1.0.
        # Usamos arredondamento para reduzir a granularidade de rede e um deadzone para estabilidade.
        for i in range(js.get_numaxes()):
            val = round(js.get_axis(i), 2)
            if abs(val) < 0.05: val = 0.0
            enviar(f"Eixo_{i}", val)

        # 2. Botões são eventos digitais; cada botão retorna 0 ou 1.
        # O código envia o estado de cada botão ao receptor para calibração e uso em tempo real.
        for i in range(js.get_numbuttons()):
            enviar(f"Botao_{i}", js.get_button(i))

        # 3. D-Pad geralmente é lido como hats no Pygame.
        # Cada hat tem dois componentes: X (horizontal) e Y (vertical).
        for i in range(js.get_numhats()):
            hat = js.get_hat(i)
            enviar(f"Hat_{i}_X", hat[0])
            enviar(f"Hat_{i}_Y", hat[1])
            
    else:
        # Tenta encontrar novamente o joystick caso ele seja desconectado.
        js = buscar_controle()

    # Mantém a janela do Pygame atualizada para evitar que o Android interrompa o processo por inatividade.
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
    # Limita o loop a 60 Hz para equilibrar responsividade com consumo de CPU.
    pygame.time.Clock().tick(60)