import pygame
import time
import os

# --- inicialização do Pygame e configuração da janela ---
pygame.init()

# Forçar o driver de vídeo do Android para evitar erros de inicialização
os.environ['SDL_VIDEODRIVER'] = 'android'

info = pygame.display.Info()
largura, altura = info.current_w, info.current_h
screen = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Calibrador Pro Bluetooth")

# Fatores de escala baseados no layout 600x900
scale_x = largura / 600
scale_y = altura / 900

def relx(x): return int(x * scale_x)
def rely(y): return int(y * scale_y)

# Fontes (Usando None para carregar a fonte padrão caso a Arial não exista no Android)
fonte_titulo = pygame.font.SysFont(None, int(35 * scale_y), bold=True)
fonte_id = pygame.font.SysFont(None, int(60 * scale_y), bold=True)
fonte_info = pygame.font.SysFont(None, int(25 * scale_y))

pygame.joystick.init()

ultimo_botao_id = "Nenhum"
js = None
nome_js = "Aguardando controle..."

def buscar_controle():
    global js, nome_js
    joystick_count = pygame.joystick.get_count()
    if joystick_count > 0:
        for i in range(joystick_count):
            temp_js = pygame.joystick.Joystick(i)
            temp_js.init()
            # Filtro: Ignora sensores de movimento/acelerômetro do Android
            if "accelerometer" not in temp_js.get_name().lower():
                js = temp_js
                nome_js = js.get_name()
                return True
    return False

def escrever(texto, x, y, cor=(255, 255, 255), fonte=None):
    if fonte is None: fonte = fonte_info
    img = fonte.render(texto, True, cor)
    screen.blit(img, (x, y))

print("Iniciando busca por controle Bluetooth...")
clock = pygame.time.Clock()

# --- Loop Principal ---
while True:
    screen.fill((20, 20, 25))
   
    # Desenha o Cabeçalho
    pygame.draw.rect(screen, (40, 40, 50), (0, 0, largura, rely(100)))
    escrever("CALIBRADOR BLUETOOTH", relx(130), rely(30), (0, 255, 150), fonte_titulo)
    escrever(f"Status: {nome_js[:25]}", relx(20), rely(110), (150, 150, 150))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Se o controle não estiver conectado, tenta buscar a cada ciclo
    if js is None:
        buscar_controle()
        escrever("POR FAVOR, CONECTE O CONTROLE", relx(100), rely(400), (255, 100, 100))
        escrever("E TOQUE NA TELA", relx(200), rely(450), (200, 200, 200))
    else:
        try:
            # Lógica de Botões
            for i in range(js.get_numbuttons()):
                if js.get_button(i):
                    ultimo_botao_id = str(i)

            # Painel do último botão
            pygame.draw.rect(screen, (50, 50, 60), (relx(50), rely(150), relx(500), rely(200)), border_radius=15)
            escrever("ÚLTIMO BOTÃO APERTADO:", relx(70), rely(170), (200, 200, 200))
            escrever(f"ID: {ultimo_botao_id}", relx(210), rely(240), (255, 255, 0), fonte_id)

            # Movimentação de Eixos
            escrever("EIXOS E GATILHOS:", relx(50), rely(400), (0, 200, 255))
            y_eixo = rely(450)
           
            for i in range(js.get_numaxes()):
                val = round(js.get_axis(i), 2)
                if abs(val) > 0.15: # Zona morta
                    pygame.draw.rect(screen, (30, 80, 120), (relx(50), y_eixo, relx(500), rely(50)), border_radius=5)
                    escrever(f"EIXO {i}", relx(70), y_eixo + rely(10), (255, 255, 255))
                    escrever(f"VALOR: {val}", relx(350), y_eixo + rely(10), (0, 255, 100))
                    y_eixo += rely(60)
       
        except pygame.error:
            # Se o controle for desconectado durante o uso
            js = None
            nome_js = "Controle desconectado!"

    escrever("Use o botão 'Voltar' para sair", relx(150), rely(850), (100, 100, 100))

    pygame.display.flip()
    clock.tick(60)