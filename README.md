# 🔍 Scanner de Backdoor para FiveM

[![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![FiveM](https://img.shields.io/badge/FiveM-Server-orange.svg)](https://fivem.net/)
[![Ryu Garage](https://img.shields.io/badge/Desenvolvido%20por-Ryu%20Garage-orange?style=flat-square)](https://github.com/ryugarage)

> **Scanner Python para detectar e remover backdoors em servidores FiveM**  
> Protege seu servidor contra código malicioso, arquivos JavaScript ofuscados e injeções em arquivos de configuração.

<div align="center">

**Desenvolvido com ❤️ por [Ryu Garage](https://github.com/ryugarage)**

[![Made with Python](https://img.shields.io/badge/Made%20with-Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FiveM](https://img.shields.io/badge/FiveM-Server-orange?style=for-the-badge)](https://fivem.net/)

</div>

## ✨ Funcionalidades

- 🔎 **Detecção Automática**: Escaneia recursivamente todo o diretório do servidor
- 🛡️ **Múltiplos Padrões**: Detecta código XOR ofuscado, arquivos suspeitos e injeções em `fxmanifest.lua`
- 🧹 **Limpeza Inteligente**: Remove apenas código malicioso, preservando arquivos legítimos
- 📊 **Relatórios Detalhados**: Gera relatórios completos de todas as detecções
- ⚙️ **Modo Interativo e Automático**: Escolha como deseja executar a limpeza
- 🔒 **Seguro**: Não modifica arquivos legítimos, apenas remove código malicioso

## 🎯 O que o Scanner Detecta

### 1. Código XOR Ofuscado
- Padrão: `x=(e,k=3)=>[...e].map(c=>String.fromCharCode(c.charCodeAt()^k))`
- Padrão alternativo: `x=s=>eval(s.replace(/\\u([0-9a-f]{4})/g,...))`
- Execução maliciosa: `globalThis[x("fubo")]`

### 2. Arquivos JavaScript Suspeitos
- Arquivos ocultos (nomes começando com ponto): `.eventHandler.js`, `.snapshot.js`, `.env.js`
- Arquivos que tentam se passar por arquivos do Git: `gitignore.js`, `gitattributes.js`, `gitconfig.js`

### 3. Injeções em fxmanifest.lua
- Linhas maliciosas com padrão: `--[[server.lua]]` seguido de muitos espaços e arquivo `.js`
- Exemplo: `--[[server.lua]]                                                                  'temp/.env.local.js'`

## 🚀 Instalação

### Requisitos
- Python 3.6 ou superior
- Windows (para arquivos `.bat`) ou qualquer sistema com Python

### Download
1. Clone ou baixe este repositório
2. Navegue até a pasta `scanner_backdoor`

## 📖 Como Usar

### Modo Interativo (Recomendado)

**Windows:**
```bash
# Duplo clique em:
scan_backdoor.bat
```

**Linux/Mac:**
```bash
python scan_backdoor.py
```

O scanner irá:
- ✅ Escanear todo o diretório
- ✅ Mostrar arquivos maliciosos encontrados
- ✅ Perguntar antes de deletar/limpar
- ✅ Gerar relatório detalhado

### Modo Automático

**Windows:**
```bash
# Duplo clique em:
scan_backdoor_auto.bat
```

**Linux/Mac:**
```bash
python scan_backdoor_auto_delete.py
```

⚠️ **ATENÇÃO**: O modo automático deleta arquivos e remove linhas maliciosas **sem confirmação**!

### Modo Dry-Run (Simulação)

Para testar sem fazer alterações:
```bash
python scan_backdoor.py --dry-run
# ou
python scan_backdoor.py -n
```

## 📁 Estrutura de Arquivos

```
scanner_backdoor/
├── scan_backdoor.py              # Script Python principal
├── scan_backdoor.bat             # Executável Windows (modo interativo)
├── scan_backdoor_auto.bat        # Executável Windows (modo automático)
├── scan_backdoor_auto_delete.py  # Script Python (modo automático)
├── README.md                     # Este arquivo
├── README_SCANNER.md             # Documentação técnica completa
└── INSTRUCOES.txt                # Instruções rápidas
```

## 📊 Relatórios

O scanner gera relatórios em formato texto com:
- Data e hora da varredura
- Diretório escaneado
- Número de arquivos e diretórios verificados
- Lista completa de arquivos maliciosos encontrados
- Arquivos `fxmanifest.lua` com linhas maliciosas
- Resultado da remoção/limpeza

**Formato do arquivo:** `relatorio_scan_YYYYMMDD_HHMMSS.txt`

## ⚙️ Configurações

Você pode personalizar o scanner editando `scan_backdoor.py`:

```python
# Extensões de arquivo para verificar
CHECK_EXTENSIONS = ['.js', '.lua']

# Pastas para ignorar
IGNORE_PATHS = [
    'node_modules',
    '.git',
    '__pycache__',
    '.vscode',
    '.idea',
]

# Tamanho máximo de arquivo para verificar (em bytes)
MAX_FILE_SIZE = 50000  # 50KB
```

## 🔒 Segurança

O scanner:
- ✅ Não modifica arquivos legítimos
- ✅ Apenas detecta padrões específicos de backdoor
- ✅ Gera relatório antes de deletar
- ✅ Pode ser executado em modo dry-run para simulação
- ✅ Remove apenas linhas maliciosas de `fxmanifest.lua`, preservando o resto do arquivo

## ⚠️ Avisos Importantes

- **Backup**: Sempre faça backup antes de executar o scanner
- **Modo Automático**: O modo automático deleta arquivos sem confirmação
- **Permissões**: Alguns arquivos podem requerer permissões administrativas
- **Teste Primeiro**: Execute em modo dry-run antes de usar em produção

## 🐛 Solução de Problemas

### Python não encontrado
```bash
# Verifique se Python está instalado
python --version

# Se não estiver instalado, baixe em: https://www.python.org/
```

### Erro de permissão
- Execute como administrador (Windows)
- Use `sudo` (Linux/Mac)

### Arquivo não pode ser deletado
- Verifique se o arquivo não está em uso
- Feche editores que possam estar usando o arquivo
- Tente executar como administrador

## 📝 Exemplos de Uso

### Escanear diretório específico
```bash
python scan_backdoor.py "C:\caminho\para\servidor"
```

### Modo interativo com confirmação
```bash
python scan_backdoor.py
# O scanner perguntará antes de cada ação
```

### Modo automático (sem perguntas)
```bash
python scan_backdoor_auto_delete.py
# Remove automaticamente tudo que encontrar
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir novas funcionalidades
- Enviar pull requests

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🙏 Agradecimentos

Desenvolvido para proteger servidores FiveM contra backdoors e código malicioso.

---

**⚠️ IMPORTANTE**: Este scanner foi desenvolvido especificamente para detectar padrões conhecidos de backdoors. Sempre mantenha backups e execute testes antes de usar em produção.

**🔗 Links Úteis**:
- [Documentação FiveM](https://docs.fivem.net/)
- [Python Documentation](https://docs.python.org/)

---

## 👨‍💻 Desenvolvido por

<div align="center">

### 🏍️ Ryu Garage

**Proteção e Segurança para Servidores FiveM**

[![Ryu Garage](https://img.shields.io/badge/Ryu%20Garage-Developer-orange?style=for-the-badge)](https://github.com/ryugarage)

*Desenvolvido com ❤️ para a comunidade FiveM*

</div>

---

⭐ **Se este projeto foi útil, considere dar uma estrela!**

