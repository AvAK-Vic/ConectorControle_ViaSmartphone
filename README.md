# 🎮 Conector de Controle via Smartphone

## 📋 Visão Geral

**ConectorControle_ViaSmartphone** é um projeto pessoal criado como experimento e aprendizado prático. Ele transforma seu smartphone Android em uma ponte de comunicação de alto desempenho para gamepads.

O celular recebe os sinais de um controle Bluetooth (Ipega, DualShock, Xbox etc.) e transmite os comandos via rede local (Wi‑Fi) para o PC, onde são convertidos em um controle virtual XInput.

Ideal para situações em que o computador não possui suporte Bluetooth nativo, ou quando se deseja estender o alcance do controle usando a rede de dados.

> ⚠️ **Aviso**: este projeto foi desenvolvido por um iniciante com auxílio de inteligência artificial. Pode apresentar bugs e não é uma solução comercial. Se o seu controle tiver um cabo USB, conectá‑lo diretamente ao PC é muito mais simples.

---

## 🎯 Como Funciona

O sistema é dividido em duas partes que se comunicam via UDP para reduzir latência:

- **Transmissor (Android):** roda no Pydroid 3. Lê eixos, botões e D‑Pad do controle físico e envia pacotes somente quando há mudança de estado.
- **Receptor (Windows):** recebe os pacotes em uma thread separada, processa os valores e injeta os comandos no Windows como um controle XInput virtual.

---

## 🗂️ Estrutura do Repositório

```
ConectorControle_ViaSmartphone/
├── README.md                  # documentação
├── Phone/
│   ├── controle.py            # transmissor (asyncio)
│   ├── calibrador.py          # visualizador/diagnóstico no Android
│   └── diagnostico.py         # script para verificar reconhecimento do joystick
└── Pc/
    └── receptor.py            # receptor multithread para Windows
```

---

## 🔧 Requisitos e Instalação

### No Computador (Windows)
1. Instale Python 3.8+.
2. Instale dependências:
   ```bash
   pip install vgamepad keyboard psutil
   ```

### No Smartphone (Android)
1. Instale o aplicativo **Pydroid 3** pela Play Store.
2. Dentro do Pydroid, abra o terminal e execute:
   ```bash
   pip install pygame
   ```

---

## 🚀 Guia de Uso Rápido

1. **Inicie o receptor no PC**
   ```bash
   python Pc/receptor.py
   ```
   Ele inicia escutando na porta UDP 5005.
   - Atalho de saída: `CTRL+Q` no teclado ou `SELECT+START` no controle.

2. **Configure o transmissor no celular**
   - Abra `Phone/controle.py` no Pydroid e edite a variável `IP_DO_PC` com o IPv4 do seu computador.
     ```python
     IP_DO_PC = "192.168.0.100"  # substitua pelo IP do PC
     ```
   - Execute: `python Phone/controle.py`.

3. **Calibre o controle**
   - Se os IDs dos botões parecerem errados, execute `Phone/calibrador.py` para ver os valores e ajuste o mapeamento em `controle.py`.
   - Caso o transmissor não reconheça o controle, rode `Phone/diagnostico.py` para diagnosticar o joystick.

---

## ⚙️ Arquitetura e Otimizações

- **Threaded listener:** o receptor utiliza uma thread dedicada para leitura de rede, evitando atraso no processamento.
- **Envio diferencial:** o transmissor só envia pacotes quando os valores mudam, economizando bateria e banda.
- **Filtro de acelerômetro:** entradas de sensoreamento de inclinação são ignoradas.
- **D‑Pad integrado:** botões físicos são convertidos em eixos do D‑Pad virtual.

---

## 🎮 Mapeamento Padrão

| Input     | Função no PC          |
|-----------|------------------------|
| AX / AY   | Analógico esquerdo     |
| RX / RY   | Analógico direito      |
| LT / RT   | Gatilhos progressivos  |
| BTN_A/B/X/Y | Botões de ação       |
| DPAD_X/Y  | Direcional (cruz)      |
| SELECT/START | Menu e opções       |


---

## 📝 Licença e Disclaimer

Projeto experimental fornecido "como está". Use por sua conta e risco. Pode conter bugs; melhorias são bem-vindas.

---

## 👤 Sobre Este Projeto

- Desenvolvido sozinho por um iniciante em Python e redes.
- Inteligência artificial foi usada para gerar partes do código e documentação.
- Objetivo: aprender sobre comunicação de redes, emulação de entrada e desenvolvimento em Python.
- Alternativa recomendada: use cabo USB sempre que possível.

---

## 📧 Contribuições

Sugestões e correções são bem-vindas! Abra uma issue ou envie um pull request.
