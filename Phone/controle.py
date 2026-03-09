import asyncio
import pygame
import socket
import time

# --- CONFIGURAÇÕES ---
IP_DO_PC = "xxx.xxx.xx.xx".strip()
PORTA = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# --- INICIALIZAÇÃO ---
pygame.init()
screen = pygame.display.set_mode((600, 900))
pygame.display.set_caption("Transmissor Versátil")
fonte = pygame.font.SysFont(None, 45)

pygame.joystick.init()

try:
    js = pygame.joystick.Joystick(0)
    js.init()
    nome_controle = js.get_name()
except:
    nome_controle = "NENHUM CONTROLE!"

last_state = {}
ultimo_comando = "Aguardando..."

async def enviar(chave, valor):
    """Só envia quando o valor muda. Executa o envio em executor para não bloquear o loop."""
    global last_state, ultimo_comando
    if last_state.get(chave) != valor:
        msg = f"{chave}:{valor}"
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, sock.sendto, msg.encode(), (IP_DO_PC, PORTA))
        last_state[chave] = valor
        # registra ativação para a tela
        if (isinstance(valor, int) and valor == 1) or (isinstance(valor, float) and abs(valor) > 0.5):
            ultimo_comando = chave

async def main():
    clock = pygame.time.Clock()
    while True:
        screen.fill((25, 25, 35))
        pygame.event.pump()
        if "js" in locals() and js.get_init():
            # --- 1. ANALÓGICOS (Eixos) ---

            await enviar("AX", round(js.get_axis(0), 2))
            await enviar("AY", round(js.get_axis(1), 2))
            await enviar("RX", round(js.get_axis(2), 2))
            await enviar("RY", round(js.get_axis(3), 2))
           
            # --- 2. GATILHOS (Eixos) ---

            await enviar("LT", max(0, round(js.get_axis(6), 2)))
            await enviar("RT", max(0, round(js.get_axis(7), 2)))

            # --- 3. BOTÕES PRINCIPAIS ---

            await enviar("BTN_A", js.get_button(0))
            await enviar("BTN_B", js.get_button(1))
            await enviar("BTN_X", js.get_button(2))
            await enviar("BTN_Y", js.get_button(3))
            await enviar("BTN_SELECT", js.get_button(4))
            await enviar("BTN_START", js.get_button(6))
            await enviar("LB", js.get_button(9))
            await enviar("RB", js.get_button(10))
            await enviar("L3", js.get_button(7))
            await enviar("R3", js.get_button(8))

            # --- 4. D-PAD ---
            dy = 0
            if js.get_button(11): dy = 1     
            elif js.get_button(12): dy = -1  

            await enviar("DPAD_Y", dy)

            dx = 0
            if js.get_button(14): dx = 1     
            elif js.get_button(13): dx = -1  
            await enviar("DPAD_X", dx)

        # --- INTERFACE VISUAL ---
        txt_ip = fonte.render(f"IP PC: {IP_DO_PC}", True, (0, 255, 150))
        txt_ctrl = fonte.render(f"Controle: {nome_controle[:15]}", True, (255, 255, 255))
        txt_cmd = fonte.render(f"Ultimo ID: {ultimo_comando}", True, (255, 255, 0))
       
        screen.blit(txt_ip, (50, 50))
        screen.blit(txt_ctrl, (50, 110))
        screen.blit(txt_cmd, (50, 200))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)


if __name__ == "__main__":
    asyncio.run(main())