# # ConectorControle_ViaSmartphone 🎮📱

Criei este projeto para jogar com controle no PC sem ter um receptor Bluetooth. O sistema utiliza um smartphone Android como ponte: o controle conecta via Bluetooth no celular, que transmite os comandos via Wi-Fi (UDP) para o PC, emulando um controle de Xbox 360 virtual com baixa latência.

## 🚀 Como funciona?
O projeto é dividido em duas partes:
1. **Transmissor (Android):** Um script Python rodando no Pydroid 3 que lê o joystick e envia pacotes UDP.
2. **Receptor (PC):** Um script Python que recebe esses pacotes e usa a biblioteca `vgamepad` para criar um controle virtual Xbox no Windows.

## 🛠️ Requisitos
- **No PC:** Python instalado e a biblioteca `vgamepad`.
- **No Android:** Aplicativo **Pydroid 3** e biblioteca `pygame`.
- **Rede:** Ambos os dispositivos devem estar conectados no **mesmo Wi-Fi**.

---

## 📖 Passo a Passo para Configuração

### 1. Conexão do Controle
Conecte seu controle (Ipega, PS4, Xbox, etc.) ao Bluetooth do celular. Certifique-se de que ele está pareado e funcional no Android.

### 2. Identificação do IP do PC
Para que o celular saiba para onde enviar os dados:
1. No teclado do computador, pressione as teclas **Windows + R**.
2. Na caixa que abrir, digite `cmd` e aperte **Enter**.
3. No terminal, digite `ipconfig` e aperte **Enter**.
4. **IMPORTANTE:** Se você usa **VPN**, Hamachi ou máquinas virtuais, aparecerão muitos IPs. Procure especificamente pela seção chamada **"Adaptador Rede Sem Fio Wi-Fi"** (ou *Wireless LAN adapter Wi-Fi*).
5. Anote o número do **Endereço IPv4** desta seção (ex: `192.168.18.15`). 



### 3. Calibração (Essencial para novos controles)
Como cada fabricante usa IDs diferentes, você deve mapear seu controle usando o script `calibrador_android.py` no app **Pydroid 3**:
1. Execute o calibrador no celular.
2. Pressione os botões e mova os analógicos.
3. **Anote os IDs:**
    * **Botões:** O ID do último botão pressionado ficará fixo na tela para facilitar a anotação. Incluindo botões como Start e Select.
    * **Analógicos:** Note que cada alavanca possui **dois eixos** (Horizontal e Vertical). Anote os números de cada eixo que se move.
    * **Gatilhos (L2/R2):** Verifique se eles aparecem como botões simples ou como eixos de pressão.

### 4. Configuração do Transmissor
1. No **Pydroid 3**, abra o arquivo `transmissor_android.py`.
2. **Mudar o IP:** Busque no início do código a linha: `IP_DO_PC = "coloque seu ip aqui"`. Substitua o texto pelo IP do Wi-Fi que você anotou no Passo 2.
3. **Mudar os IDs:** Atualize todos os IDs de botões e eixos no código conforme as anotações feitas no calibrador.
4. **IMPORTANTE (Salvar):** O Pydroid 3 **não salva as alterações automaticamente**. Clique no ícone da **Pasta** no topo da tela e selecione **Save** antes de rodar, ou suas mudanças de IP e IDs serão perdidas.

### 5. Execução Final
1. **No PC:** No seu terminal ou editor, execute o receptor: `python receptor.py`.
2. **No Android:** Com o código salvo no Pydroid 3, clique no botão **Play** (ícone amarelo).
3. Abra seu jogo no PC e divirta-se!

---

### ⚠️ Adendo de Versatilidade
Este projeto é universal, mas se você trocar de controle (ex: trocar um Ipega por um de PS4), será necessário **repetir o processo de calibração** e atualizar todos os IDs novamente no código `transmissor_android.py`, pois os mapeamentos variam drasticamente entre fabricantes.

---
*Projeto desenvolvido para resolver o problema de falta de hardware Bluetooth no computador.*
