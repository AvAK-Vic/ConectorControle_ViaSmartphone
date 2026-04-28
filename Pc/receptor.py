import importlib.util
import socket
import json
import os
import vgamepad as vg

# Configurações de rede UDP e do arquivo de calibração.
# IP_RECEPTOR = '0.0.0.0' indica que o receptor aceitará conexões de qualquer interface de rede.
# PORTA é a porta UDP usada para receber eventos do Android.
# ARQUIVO_CONFIG guarda o mapeamento entre IDs de eventos recebidos e comandos lógicos do gamepad.
IP_RECEPTOR = "0.0.0.0"
PORTA = 5005
ARQUIVO_CONFIG = "config_controle.json"

class ReceptorRequisitos:
    def __init__(self, pacote="vgamepad", arquivo_config=ARQUIVO_CONFIG, host=IP_RECEPTOR, porta=PORTA):
        self.pacote = pacote
        self.arquivo_config = arquivo_config
        self.host = host
        self.porta = porta

    def verificar(self):
        """Verifica dependências essenciais e reserva a porta UDP antes de iniciar o algoritmo.

        Esta verificação é importante para falhar cedo caso o ambiente não esteja corretamente configurado.
        O pacote `vgamepad` é necessário para criar o gamepad virtual no Windows.
        A porta UDP deve estar livre para que o receptor receba mensagens do Android.
        """
        if importlib.util.find_spec(self.pacote) is None:
            raise RuntimeError(
                f"O pacote Python '{self.pacote}' não está instalado. Execute: pip install {self.pacote}"
            )

        if not os.path.exists(self.arquivo_config):
            print(
                f"Aviso: '{self.arquivo_config}' não foi encontrado. A calibração será executada para criar o arquivo."
            )

        probe_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe_socket.bind((self.host, self.porta))
        except Exception as exc:
            raise RuntimeError(
                f"Não foi possível abrir a porta UDP {self.porta} em {self.host}: {exc}"
            )
        finally:
            probe_socket.close()

requisitos = ReceptorRequisitos().verificar()

gamepad = vg.VX360Gamepad()

MAPA_VIRTUAL = {
    "A_PULO": vg.XUSB_BUTTON.XUSB_GAMEPAD_A,
    "B_VOLTAR": vg.XUSB_BUTTON.XUSB_GAMEPAD_B,
    "X_ACAO": vg.XUSB_BUTTON.XUSB_GAMEPAD_X,
    "Y_MENU": vg.XUSB_BUTTON.XUSB_GAMEPAD_Y,
    "LB_L1": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
    "RB_R1": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
    "L3_CLICK": vg.XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
    "R3_CLICK": vg.XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
    "SELECT": vg.XUSB_BUTTON.XUSB_GAMEPAD_BACK,
    "START": vg.XUSB_BUTTON.XUSB_GAMEPAD_START,
    "DPAD_CIMA": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
    "DPAD_BAIXO": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
    "DPAD_ESQUERDA": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
    "DPAD_DIREITA": vg.XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((IP_RECEPTOR, PORTA))

def limpar_buffer():
    """Descarta mensagens UDP antigas que ainda estão aguardando no buffer do socket.

    Durante a calibração, o usuário pode apertar comandos enquanto responde ao texto na tela.
    Essas mensagens antigas não devem ser processadas por engano na etapa seguinte.
    """
    sock.setblocking(False)
    try:
        while True:
            sock.recvfrom(1024)
    except:
        pass
    sock.setblocking(True)

def calibrar():
    print("\n=== MODO DE CALIBRAÇÃO (COM LIMPEZA DE BUFFER) ===")
    mapeamento = {"botoes": {}, "eixos": {}, "dpad": {}}
    
    botoes_para_calibrar = [
        ("A_PULO", "Botão A (Inferior)"), ("B_VOLTAR", "Botão B (Direita)"),
        ("X_ACAO", "Botão X (Esquerda)"), ("Y_MENU", "Botão Y (Superior)"),
        ("LB_L1", "L1/LB"), ("RB_R1", "R1/RB"),
        ("L3_CLICK", "Clique Analógico Esquerdo"), ("R3_CLICK", "Clique Analógico Direito"),
        ("SELECT", "SELECT"), ("START", "START")
    ]
    
    eixos_para_calibrar = [
        ("ESQUERDO_HORIZONTAL", "Analógico ESQUERDO para os LADOS"),
        ("ESQUERDO_VERTICAL", "Analógico ESQUERDO para CIMA/BAIXO"),
        ("DIREITO_HORIZONTAL", "Analógico DIREITO para os LADOS"),
        ("DIREITO_VERTICAL", "Analógico DIREITO para CIMA/BAIXO"),
        ("L2_GATILHO", "Gatilho Esquerdo (L2)"), ("R2_GATILHO", "Gatilho Direito (R2)")
    ]

    def confirmar_captura(id_detectado, comando_nome):
        print(f"\n[!] Detectado ID: {id_detectado} para {comando_nome}")
        conf = input("    Pressione ENTER para aceitar ou 'r' para repetir: ").lower()
        limpar_buffer()  # Descarrega eventos antigos que podem ter sido gerados enquanto o usuário interagia.
        return conf == ""

    # Calibração de botões principais.
    # Cada pacote enviado pelo Android contém um identificador de botão e um valor binário.
    # O receptor registra apenas o ID do evento correspondente ao pressionamento desejado.
    for chave, desc in botoes_para_calibrar:
        confirmado_final = False
        limpar_buffer()
        while not confirmado_final:
            print(f"\r>> AGUARDANDO: {desc}         ", end="")
            data, _ = sock.recvfrom(1024)
            msg = data.decode()
            if "Botao" in msg:
                id_bruto, valor = msg.split(":")
                if valor == "1":
                    if confirmar_captura(id_bruto, desc):
                        mapeamento["botoes"][id_bruto] = chave
                        confirmado_final = True

    # Calibração de eixos analógicos e gatilhos.
    # O Android transmite valores contínuos para esses componentes, então usamos um limiar
    # para confirmar que o movimento foi intencional e não apenas ruído do hardware.
    for chave, desc in eixos_para_calibrar:
        confirmado_final = False
        limpar_buffer()
        while not confirmado_final:
            print(f"\r>> AGUARDANDO: {desc}         ", end="")
            data, _ = sock.recvfrom(1024)
            msg = data.decode()
            if "Eixo" in msg:
                id_bruto, valor = msg.split(":")
                # Aumentamos para 0.9 para garantir que você realmente moveu o controle
                if abs(float(valor)) > 0.9:
                    if confirmar_captura(id_bruto, desc):
                        mapeamento["eixos"][id_bruto] = chave
                        confirmado_final = True

    # Calibração da cruzeta (D-Pad) em quatro direções.
    # Diferentes controles podem enviar o D-Pad como botão, eixo ou hat, então aceitamos todos esses formatos.
    print("\n=== CALIBRANDO D-PAD (DIRECIONAIS) ===")
    dpad_direcoes = [
        ("DPAD_CIMA", "D-Pad para CIMA"),
        ("DPAD_BAIXO", "D-Pad para BAIXO"),
        ("DPAD_ESQUERDA", "D-Pad para ESQUERDA"),
        ("DPAD_DIREITA", "D-Pad para DIREITA")
    ]

    for chave, desc in dpad_direcoes:
        confirmado_final = False
        limpar_buffer()
        while not confirmado_final:
            print(f"\r>> AGUARDANDO: {desc}         ", end="")
            data, _ = sock.recvfrom(1024)
            msg = data.decode()
            
            # Aceita qualquer formato de evento compatível: botão, eixo ou hat.
            # Isso permite funcionar com controles que não seguem o mesmo esquema de nomes.
            if ":" in msg:
                id_bruto, valor = msg.split(":")
                try:
                    val_num = float(valor)
                    # Detecta pressionamento efetivo do D-Pad.
                    # Para botões digitais o valor é 1; para eixos analógicos usamos um threshold de 0.7.
                    if abs(val_num) > 0.7:
                        if confirmar_captura(id_bruto, desc):
                            mapeamento["dpad"][id_bruto] = chave
                            confirmado_final = True
                except: pass

    with open(ARQUIVO_CONFIG, 'w') as f:
        json.dump(mapeamento, f)
    return mapeamento

def carregar_config():
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, 'r') as f:
            return json.load(f)
    return None

# Fluxo principal de inicialização do receptor.
# Primeiro tentamos carregar o mapeamento de eventos de calibração existente.
# Se não existir ou se o usuário pedir, parte-se para a calibração interativa.
mapa = carregar_config()
if not mapa or input("Deseja recalibrar tudo? (s/n): ").lower() == 's':
    mapa = calibrar()

print("\n=== RECEPTOR RODANDO ===")

last_lx, last_ly = 0, 0
last_rx, last_ry = 0, 0

try:
    while True:
        data, addr = sock.recvfrom(1024)
        msg = data.decode()
        chave, valor = msg.split(":")

        nome = chave
        if chave in mapa["botoes"]: 
            nome = mapa["botoes"][chave]
        elif chave in mapa["eixos"]: 
            nome = mapa["eixos"][chave]
        elif chave in mapa["dpad"]: 
            nome = mapa["dpad"][chave]

        # Converte o evento recebido em um comando de gamepad virtual.
        # O mapeamento de calibração transforma IDs de hardware em nomes lógicos de controle.
        
        # Se o evento for um botão ou uma direção de D-Pad já calibrada
        if nome in MAPA_VIRTUAL:
            if valor == "1":
                gamepad.press_button(button=MAPA_VIRTUAL[nome])
            else:
                gamepad.release_button(button=MAPA_VIRTUAL[nome])

        # Se o evento for um eixo analógico, converte o valor flutuante em escala de 16 bits.
        elif "HORIZONTAL" in nome or "VERTICAL" in nome:
            v_calc = int(float(valor) * 32767)
            
            # Analógico Esquerdo
            if nome == "ESQUERDO_HORIZONTAL":
                last_lx = v_calc
                gamepad.left_joystick(x_value=last_lx, y_value=last_ly)
            elif nome == "ESQUERDO_VERTICAL":
                last_ly = -v_calc  # Inverte a direção vertical porque a API XUSB espera o eixo Y positivo para cima.
                gamepad.left_joystick(x_value=last_lx, y_value=last_ly)
            
            # Analógico Direito
            elif nome == "DIREITO_HORIZONTAL":
                last_rx = v_calc
                gamepad.right_joystick(x_value=last_rx, y_value=last_ry)
            elif nome == "DIREITO_VERTICAL":
                last_ry = -v_calc  # Inverte a direção vertical para compatibilidade com a emulação do Windows.
                gamepad.right_joystick(x_value=last_rx, y_value=last_ry)
        
        # Se o evento for um gatilho, converte o valor contínuo para a escala de 0-255 exigida pelo vgamepad.
        elif "GATILHO" in nome:
            v_trig = int(float(valor) * 255)
            if "L2" in nome: gamepad.left_trigger(value=max(0, v_trig))
            elif "R2" in nome: gamepad.right_trigger(value=max(0, v_trig))

        # Envia a atualização completa do controle para o Windows
        gamepad.update()

        print(f"\rComando: {nome} | Valor: {valor}                ", end="")

except KeyboardInterrupt:
    print("\nEncerrando...")
finally:
    sock.close()
    