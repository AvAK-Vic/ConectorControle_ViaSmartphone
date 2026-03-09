import asyncio
import pygame
import socket
import time
import os

# --- CONFIGURAÇÕES ---
# Substitua pelo IP que aparece no Receptor do PC
IP_DO_PC = "192.168.18.21".strip() 
PORTA = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- INICIALIZAÇÃO OTIMIZADA ---
os.environ['SDL_VIDEODRIVER'] = 'android'
pygame.init()
screen = pygame.display.set_mode((600, 900))
pygame.display.set_caption("Transmissor Pro Otimizado")
fonte = pygame.font.SysFont(None, 45)

pygame.joystick.init()

def buscar_joystick():
    pygame.joystick.quit()
    pygame.joystick.init()
    if pygame.joystick.get_count() > 0:
        for i in range(pygame.joystick.get_count()):
            joy = pygame.joystick.Joystick(i)
            joy.init()
            if "accelerometer" not in joy.get_name().lower():
                return joy
    return None

js = buscar_joystick()
nome_controle = js.get_name() if js else "NENHUM CONTROLE!"

last_state = {}
ultimo_comando = "Aguardando..."

# Otimização: Função de envio direta (UDP não bloqueia)
def enviar(chave, valor):
    global last_state, ultimo_comando
    if last_state.get(chave) != valor:
        msg = f"{chave}:{valor}"
        try:
            sock.sendto(msg.encode(), (IP_DO_PC, PORTA))
            last_state[chave] = valor
            if valor == 1 or (isinstance(valor, float) and abs(valor) > 0.5):
                ultimo_comando = chave
        except:
            pass

async def main():
    global js, nome_controle
    clock = pygame.time.Clock()
    
    while True:
        screen.fill((25, 25, 35))
        pygame.event.pump()

        # Tenta reconectar se o controle for perdido
        if not js or not js.get_init():
            js = buscar_joystick()
            nome_controle = js.get_name() if js else "PROCURANDO..."
        
        if js:
            # 1. ANALÓGICOS (Eixos)
            enviar("AX", round(js.get_axis(0), 2))
            enviar("AY", round(js.get_axis(1), 2))
            enviar("RX", round(js.get_axis(2), 2))
            enviar("RY", round(js.get_axis(3), 2))
            
            # 2. GATILHOS (LT e RT)
            enviar("LT", max(0, round(js.get_axis(6), 2)))
            enviar("RT", max(0, round(js.get_axis(7), 2)))

            # 3. BOTÕES PRINCIPAIS
            enviar("BTN_A", js.get_button(0))
            enviar("BTN_B", js.get_button(1))
            enviar("BTN_X", js.get_button(2))
            enviar("BTN_Y", js.get_button(3))
            enviar("BTN_SELECT", js.get_button(4))
            enviar("BTN_START", js.get_button(6))
            enviar("LB", js.get_button(9))
            enviar("RB", js.get_button(10))
            enviar("L3", js.get_button(7))
            enviar("R3", js.get_button(8))

            # 4. D-PAD (BOTÕES 11 A 14)
            dy = 0
            if js.get_button(11): dy = 1   # Cima
            elif js.get_button(12): dy = -1 # Baixo
            enviar("DPAD_Y", dy)

            dx = 0
            if js.get_button(14): dx = 1   # Direita
            elif js.get_button(13): dx = -1 # Esquerda
            enviar("DPAD_X", dx)

        # INTERFACE VISUAL
        screen.blit(fonte.render(f"IP PC: {IP_DO_PC}", True, (0, 255, 150)), (50, 50))
        screen.blit(fonte.render(f"CONTROLE: {nome_controle[:18]}", True, (255, 255, 255)), (50, 110))
        screen.blit(fonte.render(f"ULTIMO: {ultimo_comando}", True, (255, 255, 0)), (50, 200))

        pygame.display.flip()
        clock.tick(60) # Mantém 60 FPS estáveis
        await asyncio.sleep(0.001) # Cede tempo para o sistema Android

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Encerrado.")