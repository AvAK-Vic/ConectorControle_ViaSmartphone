import pygame
import time

# --- inicialização do Pygame e configuração da janela ---
pygame.init()
# em dispositivos Android a tela pode ter qualquer resolução. usamos
# pygame.display.Info() para descobrir as dimensões atuais e abrir a
# janela/fullscreen com esse tamanho.
info = pygame.display.Info()
largura, altura = info.current_w, info.current_h
# opcionalmente poderíamos usar pygame.FULLSCREEN ou RESIZABLE;
# aqui mantemos a janela normal, mas já adaptada ao tamanho do display.
screen = pygame.display.set_mode((largura, altura))  # superfície de desenho
pygame.display.set_caption("Calibrador Pro")        # título da janela
# calculamos fatores de escala com base no layout original (600×900)
scale_x = largura / 600
scale_y = altura / 900

# helper para converter coordenadas 'design' em valores reais
# pode ser usado para multiplicar qualquer valor X/Y.
def relx(x):
    return int(x * scale_x)
def rely(y):
    return int(y * scale_y)

# fontes utilizadas em diferentes tamanhos / estilos
# nota: se a resolução for muito grande, talvez seja desejável escalar
# o tamanho da fonte também; aqui mantemos os tamanhos fixos por simplicidade.
fonte_titulo = pygame.font.SysFont("Arial", 35, bold=True)
fonte_id = pygame.font.SysFont("Arial", 60, bold=True)
fonte_info = pygame.font.SysFont("Arial", 25)

pygame.joystick.init()  # prepara o módulo de joystick do pygame

# estados que permanecem entre quadros
ultimo_botao_id = "Nenhum"     # guarda o último botão pressionado
# eixos_ativos era usado para memória, mas não está em uso; mantido por compatibilidade

# função auxiliar para desenhar texto na tela
def escrever(texto, x, y, cor=(255, 255, 255), fonte=None):
    if fonte is None:
        fonte = fonte_info                # usar fonte padrão se não foi passada
    img = fonte.render(texto, True, cor)  # renderiza a string como superfície
    screen.blit(img, (x, y))             # desenha na posição especificada

# tentativa de conectar o primeiro gamepad encontrado
try:
    js = pygame.joystick.Joystick(0)
    js.init()
    nome_js = js.get_name()
except Exception:                         # captura qualquer falha sem travar
    nome_js = "Conecte o controle!"      # mensagem mostrada na tela

print("Calibrador rodando...")

# relógio para limitar a taxa de frames e economizar CPU/bateria
clock = pygame.time.Clock()

# loop principal de atualização da interface
while True:
    screen.fill((20, 20, 25))  # limpa a tela para dar contraste ao texto

    # cabeçalho estático
    pygame.draw.rect(screen, (40, 40, 50), (0, 0, largura, rely(100)))
    escrever("CALIBRADOR DE GAMEPAD", relx(130), rely(30), (0, 255, 150), fonte_titulo)

    # coletar eventos apenas uma vez por ciclo, em vez de chamar pump() isoladamente
    for event in pygame.event.get():
        if event.type == pygame.QUIT:     # usuário clicou no X da janela
            pygame.quit()
            exit()

    if "js" in locals():
        # cada botão pressionado atualiza `ultimo_botao_id`
        for i in range(js.get_numbuttons()):
            if js.get_button(i):
                ultimo_botao_id = str(i)

        # desenha retângulo e texto fixo para mostrar o último botão
        pygame.draw.rect(screen, (50, 50, 60), (relx(50), rely(150), relx(500), rely(200)), border_radius=15)
        escrever("ÚLTIMO BOTÃO APERTADO:", relx(70), rely(170), (200, 200, 200))
        escrever(f"ID: {ultimo_botao_id}", relx(210), rely(220), (255, 255, 0), fonte_id)

        # mostra movimentos de eixos apenas quando saem da zona morta
        escrever("MOVIMENTAÇÃO DE EIXOS:", relx(50), rely(400), (0, 200, 255))
        y_eixo = rely(450)
        for i in range(js.get_numaxes()):
            val = round(js.get_axis(i), 2)
            if abs(val) > 0.15:                # filtra flutuações pequenas
                pygame.draw.rect(screen, (30, 80, 120), (relx(50), y_eixo, relx(500), rely(50)), border_radius=5)
                escrever(f"EIXO {i}", relx(70), y_eixo + rely(10), (255, 255, 255))
                escrever(f"VALOR: {val}", relx(350), y_eixo + rely(10), (0, 255, 100))
                y_eixo += rely(60)

    # mensagem de instrução sempre mostrada
    escrever("Toque no 'X' ou use o comando de fechar para sair", relx(110), rely(850), (100, 100, 100))

    pygame.display.flip()          # atualiza o conteúdo da janela na tela
    clock.tick(60)                 # limita a 60 quadros por segundo

