# Conector de Controle Android para PC via Wi-Fi

Este projeto transforma um controle físico ou joystick conectado ao Android em um gamepad virtual para Windows.
Ele usa UDP para transmitir eventos do Android ao PC e `vgamepad` para emular um Xbox 360 virtual no Windows.

## ✅ Vantagens

- Emulação nativa de Xbox 360 para compatibilidade ampla com jogos Windows.
- Transmissão UDP leve e de baixa latência.
- Mapeamento e calibração dinâmicos de botões, eixos e D-Pad.
- Evita repetição de comandos ao enviar apenas mudanças de estado.
- Suporta joystick Bluetooth ou USB detectado pelo `pygame` no Android.
- Não exige instalação de drivers extras no Android além do Pydroid 3.
- O mapeamento é gravado em `config_controle.json` para reutilização.

## 🎯 Para quem foi feito

- Usuários que desejam usar um joystick Android como controle de jogos no Windows.
- Pessoas com um controle Bluetooth/USB conectado ao Android e que não querem usar soluções de hardware adicionais.
- Projetos de prototipagem que precisam de uma interface de controle remota baseada em Python.

> Nota: o lado Android só está escrito para execução em Pydroid 3 e depende do `pygame` para ler entradas de joystick.

## 🔧 Como funciona

### Arquitetura

1. **`Phone/controle.py`**
   - Detecta o dispositivo de entrada no Android através do `pygame`.
   - Lê eixos, botões e o D-Pad.
   - Envia pacotes UDP para o PC com o formato `Chave:Valor`.

2. **`Pc/receptor.py`**
   - Escuta pacotes UDP na porta `5005`.
   - Realiza calibração dos IDs de botões, eixos e D-Pad.
   - Converte esses dados em comandos do gamepad virtual usando `vgamepad`.

## 🛠️ Requisitos

### No PC

- Python 3.x.
- Biblioteca `vgamepad`: `pip install vgamepad`.
- Windows com suporte a dispositivos de gamepad virtuais.
- Porta UDP `5005` livre.
- Permissão para criar/ler `config_controle.json` na pasta do projeto.

### No Android

- Pydroid 3 instalado.
- `pygame` instalado no Pydroid: `pip install pygame`.
- Um joystick ou controle conectado ao Android via USB/OTG ou Bluetooth.
- Mesmo Wi-Fi entre Android e PC.

## ⚠️ Limitações

- A emulação `vgamepad` funciona apenas no Windows.
- Dependendo do controle e do Android, nem todos os dispositivos são reconhecidos corretamente pelo `pygame`.
- O protocolo usa UDP sem confirmação, então pacotes podem ser perdidos.
- O projeto suporta basicamente um dispositivo de controle por vez.
- A calibração é manual e pode precisar ser refeita ao trocar o controle.
- Não há criptografia ou autenticação na comunicação.

## 🚀 Como usar

### 1. Preparar o PC

1. Abra um terminal na pasta `Pc`.
2. Instale `vgamepad`: `pip install vgamepad`.
3. Execute `python receptor.py`.
4. Se o arquivo `config_controle.json` não existir ou se desejar recalibrar, responda `s` à pergunta.

### 2. Preparar o Android

1. Abra `Phone/controle.py` no Pydroid 3.
2. Altere `IP_DO_PC` para o IP local do PC.
3. Execute o script.

### 3. Jogar

- Com o receptor ativo, o Android enviará eventos para o PC.
- O Windows receberá o dispositivo como um controle Xbox 360 virtual.
- Teste em seu jogo favorito.

## 📘 Observações técnicas

- `Phone/controle.py` usa `pygame.event.pump()` para manter o loop ativo e evitar que o processo seja interrompido.
- O código do Android faz debounce em valores menores que `0.05` e preserva a tela ativa para evitar suspensão.
- `Pc/receptor.py` mantém o último valor dos eixos e atualiza apenas quando necessário.
- O arquivo `config_controle.json` armazena o mapeamento entre IDs de eventos do joystick Android e nomes lógicos de botões.

## 📌 Requisito no código

O `Pc/receptor.py` agora verifica automaticamente:

- se o pacote Python `vgamepad` está instalado;
- se `config_controle.json` existe ou precisa ser criado;
- se a porta UDP `5005` está disponível.

Essa validação é feita antes da criação do socket principal, evitando erros de ambiente durante a execução.

## 📂 Estrutura do projeto

- `Pc/receptor.py` — receptor UDP e emulador de gamepad.
- `Phone/controle.py` — emissor UDP no Android.
- `config_controle.json` — mapeamento gerado pela calibração.
- `README.md` — documentação do projeto.

## 💡 Dicas

- Use uma rede Wi-Fi estável para reduzir perda de pacotes.
- Verifique o IP do PC com `ipconfig` e atualize `IP_DO_PC` no Android.
- Se o controle não aparecer no Windows, reinicie o receptor e refaça a calibração.
