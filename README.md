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

### 📋 Requisitos

Antes de usar o scanner, certifique-se de ter:

- ✅ **Python 3.6 ou superior** instalado
  - Verifique se está instalado: `python --version` ou `python3 --version`
  - Se não tiver, baixe em: [https://www.python.org/downloads/](https://www.python.org/downloads/)
  - **Importante**: Durante a instalação, marque a opção "Add Python to PATH"
- ✅ **Windows** (para usar os arquivos `.bat`) ou qualquer sistema com Python
- ✅ **Acesso de leitura/escrita** ao diretório do servidor
- ✅ **Permissões administrativas** (recomendado, para poder deletar arquivos protegidos)

### 📁 Estrutura de Pastas e Onde Colocar

#### ⚠️ IMPORTANTE: Onde Colocar o Scanner

O scanner **DEVE** estar na **pasta raiz do servidor FiveM**, no mesmo nível das pastas `resources`, `artifacts`, `teste`, etc.

**Por quê?** O scanner escaneia a pasta pai (onde está `resources`, `artifacts`, etc.), por isso ele precisa estar na pasta raiz do servidor.

#### ✅ Estrutura Correta:

```
E:\Bases\                    ← PASTA RAIZ DO SERVIDOR
├── resources\                         ← Pasta de recursos
├── artifacts\                         ← Pasta de artefatos
├── teste\                            ← Outras pastas do servidor
├── server.cfg                         ← Arquivos de configuração
├── server.bat                         ← Scripts do servidor
└── scanner_backdoor\                  ← 📁 PASTA DO SCANNER (AQUI!)
    ├── scan_backdoor.py
    ├── scan_backdoor.bat
    ├── scan_backdoor_auto.bat
    ├── scan_backdoor_auto_delete.py
    ├── README.md
    └── INSTRUCOES.txt
```

#### ❌ Estrutura INCORRETA (NÃO coloque assim):

```
E:\Bases\
├── resources\
│   └── scanner_backdoor\              ← ❌ ERRADO! Não coloque aqui
```

### 📝 Passos para Instalação:

1. **Baixe ou clone este repositório**
   - Se baixou como ZIP, extraia o arquivo
   - Se clonou, você já tem a pasta `scanner_backdoor`

2. **Mova a pasta `scanner_backdoor` para a pasta raiz do seu servidor FiveM**
   - A pasta raiz é onde estão as pastas `resources`, `artifacts`, `server.cfg`, etc.
   - **IMPORTANTE**: A pasta `scanner_backdoor` deve estar no mesmo nível que a pasta `resources`
   - Não coloque dentro de `resources` ou em qualquer outra pasta

3. **Verifique se Python está instalado:**
   ```bash
   python --version
   # ou
   python3 --version
   ```
   - Se aparecer um erro, instale o Python primeiro

4. **Teste o scanner (opcional):**
   ```bash
   cd scanner_backdoor
   python scan_backdoor.py --dry-run
   ```

### 🎯 Exemplo Prático:

Se seu servidor está em `C:\FiveM\MeuServidor\`, a estrutura deve ser:

```
C:\FiveM\MeuServidor\
├── resources\
├── artifacts\
├── server.cfg
└── scanner_backdoor\          ← Coloque aqui!
    ├── scan_backdoor.py
    └── scan_backdoor.bat
```

### 🔧 Como Funciona:

1. **O scanner detecta sua localização**: Quando você executa o script, ele identifica que está dentro da pasta `scanner_backdoor`

2. **Escaneia a pasta pai**: O scanner sobe um nível (pasta pai) e escaneia tudo que está lá, incluindo:
   - `resources/` (e todas as subpastas)
   - `artifacts/` (e todas as subpastas)
   - `teste/` (e todas as subpastas)
   - Qualquer outra pasta no mesmo nível

3. **Detecta padrões maliciosos**: Procura por:
   - Código XOR ofuscado em arquivos `.js`
   - Arquivos com nomes suspeitos (começando com ponto ou imitando arquivos Git)
   - Linhas maliciosas em arquivos `fxmanifest.lua`

4. **Gera relatório**: Cria um arquivo de relatório na pasta raiz do servidor com todos os achados

5. **Remove (se confirmado)**: Deleta arquivos maliciosos e limpa linhas suspeitas de `fxmanifest.lua`

## 📖 Como Usar

### 🎯 Passo a Passo Básico

1. **Navegue até a pasta `scanner_backdoor`**:
   ```bash
   cd scanner_backdoor
   ```

2. **Execute o scanner** (escolha um dos modos abaixo)

3. **Aguarde o scan terminar** - O scanner mostrará o progresso

4. **Revise os resultados** - Veja o relatório gerado

### Modo Interativo (Recomendado)

Este é o modo mais seguro, pois pergunta antes de cada ação.

**Windows:**
```bash
# Opção 1: Duplo clique no arquivo
scan_backdoor.bat

# Opção 2: Pelo terminal
cd scanner_backdoor
scan_backdoor.bat
```

**Linux/Mac:**
```bash
cd scanner_backdoor
python scan_backdoor.py
```

**O que acontece:**
1. ✅ O scanner inicia e mostra um banner
2. ✅ Escaneia todo o diretório raiz do servidor (onde está a pasta `scanner_backdoor`)
3. ✅ Mostra arquivos maliciosos encontrados (se houver)
4. ✅ Mostra linhas maliciosas em `fxmanifest.lua` (se houver)
5. ✅ **Pergunta antes de deletar cada arquivo**: "Deseja deletar [arquivo]? (s/n)"
6. ✅ **Pergunta antes de limpar cada `fxmanifest.lua`**: "Deseja limpar [arquivo]? (s/n)"
7. ✅ Remove apenas o que você confirmar
8. ✅ Gera relatório detalhado na pasta raiz do servidor

**Vantagens:**
- Você tem controle total sobre o que é deletado
- Pode revisar cada arquivo antes de remover
- Mais seguro para uso em produção

### Modo Automático

Este modo remove automaticamente tudo que encontrar, **sem perguntar**.

**Windows:**
```bash
# Opção 1: Duplo clique no arquivo
scan_backdoor_auto.bat

# Opção 2: Pelo terminal
cd scanner_backdoor
scan_backdoor_auto.bat
```

**Linux/Mac:**
```bash
cd scanner_backdoor
python scan_backdoor_auto_delete.py
```

**O que acontece:**
1. ✅ O scanner inicia e mostra um banner
2. ✅ Escaneia todo o diretório raiz do servidor
3. ✅ Mostra arquivos maliciosos encontrados
4. ✅ **Deleta automaticamente** todos os arquivos maliciosos encontrados
5. ✅ **Remove automaticamente** todas as linhas maliciosas de `fxmanifest.lua`
6. ✅ Gera relatório detalhado

⚠️ **ATENÇÃO**: 
- Este modo **NÃO PERGUNTA** antes de deletar
- Use apenas se tiver certeza do que está fazendo
- **SEMPRE faça backup antes de usar este modo**
- Recomendado apenas para uso após testar com o modo interativo

### Modo Dry-Run (Simulação)

Este modo apenas **simula** o scan, sem fazer nenhuma alteração. Perfeito para testar!

**Como usar:**
```bash
cd scanner_backdoor
python scan_backdoor.py --dry-run
# ou
python scan_backdoor.py -n
```

**O que acontece:**
1. ✅ Escaneia todo o diretório
2. ✅ Mostra o que **seria** deletado (mas não deleta)
3. ✅ Mostra o que **seria** limpo (mas não limpa)
4. ✅ Gera relatório mostrando o que seria feito
5. ✅ **Nenhum arquivo é modificado ou deletado**

**Quando usar:**
- Para testar o scanner pela primeira vez
- Para verificar se há backdoors sem fazer alterações
- Para revisar o que seria removido antes de executar de verdade

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
- Verifique se o arquivo não está com permissões de somente leitura

### Scanner não encontra arquivos
- **Verifique se o scanner está na pasta raiz do servidor**
  - A pasta `scanner_backdoor` deve estar no mesmo nível que `resources`, `artifacts`, etc.
  - Não deve estar dentro de `resources` ou qualquer outra pasta
- **Certifique-se de que está executando a partir da pasta `scanner_backdoor`**
  - Use `cd scanner_backdoor` antes de executar
- **O scanner escaneia a pasta pai** (onde está `resources`, `artifacts`, etc.)
  - Se você colocar o scanner em outro lugar, ele não vai escanear o servidor corretamente
- **Verifique se o caminho está correto**:
  ```bash
  # No Windows, verifique onde você está:
  cd
  # Deve mostrar algo como: E:\Bases\LongBeach\scanner_backdoor
  ```

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

