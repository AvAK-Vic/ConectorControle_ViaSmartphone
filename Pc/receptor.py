import socket
import vgamepad as vg
import sys
import keyboard  # para atalho de saída
import threading
import queue
import time

# --- CONFIGURAÇÃO INICIAL ----------------------------------------------------
PORTA_UDP = 5005
COMBINACAO_SAIDA = 'ctrl+q'  # combinação de teclado para encerrar o receptor

# 1. ESTADO COMPLETO DO CONTROLE ------------------------------------------------
# guarda valores atuais (analógicos, gatilhos, botões, dpad) recebidos do
# transmissor no smartphone.
estado_controle = {
    "AX": 0.0, "AY": 0.0, "RX": 0.0, "RY": 0.0,
    "LT": 0.0, "RT": 0.0,
    "BTN_A": 0, "BTN_B": 0, "BTN_X": 0, "BTN_Y": 0,
    "RB": 0, "LB": 0,
    "BTN_SELECT": 0, "BTN_START": 0,
    "L3": 0, "R3": 0,
    "DPAD_X": 0, "DPAD_Y": 0
}

# 2. MAPEAMENTO PARA CONTROLE VIRTUAL ----------------------------------------
# dicionário imutável que associa chaves de rede a botões XInput
mapeamento_botoes = {
    "BTN_A": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "BTN_B": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "BTN_X": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "BTN_Y": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "RB": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "LB": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "BTN_SELECT": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    "BTN_START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    "L3": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    "R3": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB
}

# inicializa o gamepad virtual e o socket UDP não bloqueante
gamepad = vg.VX360Gamepad()
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', PORTA_UDP))
sock.setblocking(False)  # modo não bloqueante para evitar travar o loop

# fila thread-safe para mensagens recebidas
msg_queue = queue.Queue()

# thread dedicada à leitura da rede para liberar o loop principal e evitar
# que várias leituras sucessivas causem atrasos no processamento do gamepad

def network_listener(sock, q):
    """Recebe pacotes UDP e coloca os dados brutos na fila."""
    while True:
        try:
            data, addr = sock.recvfrom(1024)  # pode lançar BlockingIOError
            q.put(data)
        except BlockingIOError:
            # sem dados no momento; dá uma pequena pausa para não girar em CPU 100%
            time.sleep(0.005)
            continue

# dispara a thread de rede em background
listener = threading.Thread(target=network_listener, args=(sock, msg_queue), daemon=True)
listener.start()

print('--- RECEPTOR DE CONTROLE SMARTPHONE ---')
print(f'🎮 Status: Online na porta {PORTA_UDP}')
print(f'⌨️  Atalho para encerrar no PC: [{COMBINACAO_SAIDA.upper()}]')

clock = time.time  # placeholder caso queiramos limitar FPS; não crítico aqui

try:
    while True:
        # checa atalho uma vez por ciclo em vez de cada recv
        if keyboard.is_pressed(COMBINACAO_SAIDA):
            print(f"\n🛑 Atalho [{COMBINACAO_SAIDA}] detectado. Encerrando...")
            break

        # processa todas as mensagens que chegaram
        while not msg_queue.empty():
            raw = msg_queue.get()
            try:
                mensagem = raw.decode('utf-8')
                if ':' in mensagem:
                    tipo, valor = mensagem.split(':')
                    if tipo in estado_controle:
                        estado_controle[tipo] = float(valor)
            except (UnicodeDecodeError, ValueError):
                # ignora pacotes malformados sem quebrar o loop
                continue

        # 4. ATUALIZAÇÃO DOS ANALÓGICOS E GATILHOS -------------------------------
        gamepad.left_joystick_float(x_value_float=estado_controle["AX"],
                                   y_value_float=-estado_controle["AY"])
        gamepad.right_joystick_float(x_value_float=estado_controle["RX"],
                                    y_value_float=-estado_controle["RY"])
        gamepad.left_trigger_float(value_float=estado_controle["LT"])
        gamepad.right_trigger_float(value_float=estado_controle["RT"])

        # 5. ATUALIZAÇÃO DOS BOTÕES SIMPLES -------------------------------------
        for chave, botao_virtual in mapeamento_botoes.items():
            if estado_controle[chave] == 1:
                gamepad.press_button(button=botao_virtual)
            else:
                gamepad.release_button(button=botao_virtual)

        # 6. ATUALIZAÇÃO DO D-PAD ------------------------------------------------
        # vertical
        if estado_controle["DPAD_Y"] == 1:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        elif estado_controle["DPAD_Y"] == -1:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
        else:
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP)
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN)
        # horizontal
        if estado_controle["DPAD_X"] == 1:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
        elif estado_controle["DPAD_X"] == -1:
            gamepad.press_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
        else:
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT)
            gamepad.release_button(vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT)

        # 7. SINCRONIZAÇÃO -------------------------------------------------------
        gamepad.update()

        # atalho de segurança: Select + Start ordem não importa
        if estado_controle["BTN_SELECT"] == 1 and estado_controle["BTN_START"] == 1:
            print("\n🛑 Combo no controle recebido. Encerrando...")
            break

        # pequena pausa para evitar 100% de CPU (cerca de 5 ms)
        time.sleep(0.005)

except KeyboardInterrupt:
    print("\nEncerrado manualmente (Ctrl+C).")
finally:
    # limpa estado do gamepad virtual antes de sair
    gamepad.reset()
    gamepad.update()
    sock.close()
    print("✨ Recursos liberados.")
    sys.exit()