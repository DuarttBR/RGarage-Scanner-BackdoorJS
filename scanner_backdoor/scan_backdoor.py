#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                             ║
║                    🔍 SCANNER DE BACKDOOR PARA FIVEM                       ║
║                                                                             ║
║                    Detecta e Remove Arquivos Maliciosos                     ║
║                    Detecta código ofuscado XOR em arquivos JavaScript       ║
║                                                                             ║
║                    ╔═══════════════════════════════════╗                   ║
║                    ║   🏍️  Desenvolvido por          ║                   ║
║                    ║      RYU GARAGE                  ║                   ║
║                    ║                                  ║                   ║
║                    ║   Proteção e Segurança           ║                   ║
║                    ║   para Servidores FiveM          ║                   ║
║                    ╚═══════════════════════════════════╝                   ║
║                                                                             ║
║                    Desenvolvido com ❤️ para a comunidade FiveM              ║
║                                                                             ║
╚═══════════════════════════════════════════════════════════════════════════╝
"""

import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Forçar UTF-8 no terminal Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Padrões de detecção em arquivos .js
# ---------------------------------------------------------------------------
# Variante antiga (mantida para compatibilidade retroativa)
JS_PATTERNS_LEGACY = [
    r'x=\(e,k=3\)=>\[\.\.\.e\]\.map\(c=>String\.fromCharCode\(c\.charCodeAt\(\)\^k\)\)',
    r'x=s=>eval\(s\.replace\(/\\\\u\(\[0-9a-f\]\{4\}\)/g',
    r'globalThis\[x\("fubo"\)\]',
    r'/\*\s*\[\s*[^\]]+\s*\]\s*\*/.*x=\(e,k=3\)',
    r'/\*\s*\[\s*[^\]]+\s*\]\s*\*/.*x=s=>eval',
]

# Variante atual: XOR com prefixo "kmm" + fromCharCode
# Padrão: (function(){const kmmXXXXX=N;function dmmXXXXX(a,k){...String.fromCharCode(a[i]^k)...}
JS_PATTERNS_CURRENT = [
    # Função auto-executável iniciada com const kmm
    r'\(function\(\)\{const\s+kmm\w+\s*=\s*\d+',
    # Variável com prefixo kmm + uso de fromCharCode XOR
    r'const\s+kmm\w+\s*=\s*\d+.*String\.fromCharCode',
    # Função decodificadora XOR com array de inteiros
    r'function\s+\w+\(a,k\)\{var\s+s=\'\'\;for\(var\s+i=0',
    # Array de inteiros XOR com fromCharCode (assinatura compacta)
    r'String\.fromCharCode\(a\[i\]\^k\)',
    # Array longo de inteiros (>= 10 valores) típico de payload XOR
    r'const\s+\w+=\[(\d{2,3},){9,}\d{2,3}\]',
]

MALICIOUS_PATTERNS = JS_PATTERNS_LEGACY + JS_PATTERNS_CURRENT

# ---------------------------------------------------------------------------
# Padrões de detecção em arquivos .lua
# ---------------------------------------------------------------------------

# Padrão 1: load() executando O MESMO PARÂMETRO recebido de evento de rede
# Detecta: AddEventHandler('evento', function(PARAM) ... load(PARAM)() ... end)
# O backreference \1 garante que só flagra quando load() executa o param do handler
# Isso é execução remota de código (RCE) nos clientes
LUA_NET_LOAD_RCE = re.compile(
    r'AddEventHandler\s*\([^,]+,\s*function\s*\(\s*(\w+)\b[^)]*\)'
    r'.*?'
    r'(?:assert\s*\(\s*)?load\s*\(\s*\1\s*\)\s*\)?\s*\(\)',
    re.DOTALL | re.IGNORECASE
)

# Padrão 2: Luraph/obfuscadores em arquivos que NÃO são de scripts pagos conhecidos
LUA_OBFUSCATED_MARKER = re.compile(
    r'--\s*This file was (?:protected|generated) using (?:Luraph|Prometheus|Alcatraz|obfusc)',
    re.IGNORECASE
)

# Prefixos de pastas de scripts pagos onde obfuscação é esperada (legítimo)
TRUSTED_OBFUSCATED_PREFIXES = [
    'xd_', 'xd-',          # XD Scripts
    'zo_', 'zo-',          # ZO Scripts
    'lb-', 'lb_',          # LB Scripts
    'wn', 'warn',          # WarnZera/WN Scripts
    'ox_', 'ox-',          # OX Scripts
    'loaf_', 'loaf-',      # Loaf Scripts
    'qb-', 'qb_',          # QB Scripts
    'es_', 'esx_',         # ESX Scripts
    'ps-', 'ps_',          # Project Sloth
    'cd_', 'cd-',          # CD Scripts
    'codem-',              # CodeM
    'renewed-',            # Renewed Scripts
    'bl_', 'bl-',          # BL Scripts
    'okokBanking', 'okokNotify', 'okokTextUI',  # OKOK Scripts
]

# ---------------------------------------------------------------------------
# Padrões de detecção em fxmanifest.lua
# ---------------------------------------------------------------------------
# Bloco shared_scripts ou server_scripts que contém arquivos .js injetados
MANIFEST_INJECT_PATTERN = re.compile(
    r'(shared_scripts|server_scripts)\s*\{[^}]*\.js[^}]*\}',
    re.IGNORECASE | re.DOTALL
)

# Linha de comentário usada pelo ColdGG Dumper (marca do vetor de infecção)
COLDGG_MARKER = re.compile(r'ColdGG\s*Dumper', re.IGNORECASE)

# Padrão antigo de injeção via comentário Lua
MANIFEST_LEGACY_PATTERN = re.compile(
    r'--\[\[server\.lua\]\]\s+[\'"](.*\.js)[\'"]'
)

# ---------------------------------------------------------------------------
# Configurações gerais
# ---------------------------------------------------------------------------
CHECK_EXTENSIONS = ['.js', '.lua']

IGNORE_PATHS = [
    'node_modules',
    '.git',
    '__pycache__',
    '.vscode',
    '.idea',
    'scanner_backdoor',   # nunca escanear a si mesmo
    'artifacts',          # binários do servidor FiveM - não tocar
]

SUSPICIOUS_FILENAMES = [
    'gitignore.js', '.gitignore.js',
    'gitattributes.js', '.gitattributes.js',
    'gitconfig.js', '.gitconfig.js',
    'gitkeep.js', '.gitkeep.js',
    'gitmodules.js', '.gitmodules.js',
    'githooks.js', '.githooks.js',
]

MAX_FILE_SIZE = 500_000  # 500KB (aumentado para cobrir arquivos maiores)


class BackdoorScanner:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.malicious_files = []          # arquivos JS a deletar
        self.malicious_manifests = []      # (path, blocos_maliciosos) de fxmanifest.lua a limpar
        self.suspicious_lua = []           # (path, motivo) arquivos Lua suspeitos (avisos)
        self.scanned_files = 0
        self.scanned_dirs = 0

    # ------------------------------------------------------------------
    # Utilitários
    # ------------------------------------------------------------------

    def should_ignore(self, path):
        path_str = str(path)
        for ignore in IGNORE_PATHS:
            if ignore in path_str:
                return True
        return False

    def is_suspicious_filename(self, file_path):
        name_lower = file_path.name.lower()
        return any(s.lower() in name_lower or name_lower == s.lower()
                   for s in SUSPICIOUS_FILENAMES)

    def read_file(self, file_path):
        """Lê arquivo de forma segura; retorna None se falhar ou for grande demais."""
        try:
            if file_path.stat().st_size > MAX_FILE_SIZE:
                return None
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Detecção de JS malicioso
    # ------------------------------------------------------------------

    def is_malicious_js(self, file_path):
        """Retorna True se o arquivo JS contiver código XOR/backdoor."""
        if self.is_suspicious_filename(file_path):
            return True

        content = self.read_file(file_path)
        if content is None:
            return False

        for pattern in MALICIOUS_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                return True
        return False

    # ------------------------------------------------------------------
    # Detecção de Lua suspeito
    # ------------------------------------------------------------------

    def is_trusted_obfuscated_path(self, file_path):
        """Retorna True se o arquivo está em pasta de script pago conhecido."""
        path_str = str(file_path).replace('\\', '/').lower()
        for prefix in TRUSTED_OBFUSCATED_PREFIXES:
            # Verifica se algum segmento do path começa com o prefixo
            if any(part.startswith(prefix.lower())
                   for part in path_str.split('/')):
                return True
        return False

    def check_lua_backdoor(self, file_path):
        """
        Analisa arquivo .lua em busca de padrões de backdoor.
        Retorna lista de (tipo, descricao) ou lista vazia.
        """
        findings = []
        content = self.read_file(file_path)
        if content is None:
            return findings

        # 1. load() executando o parâmetro do handler de evento de rede (RCE)
        for match in LUA_NET_LOAD_RCE.finditer(content):
            param = match.group(1)
            findings.append((
                'LUA_RCE',
                f'AddEventHandler executa load({param})() — '
                f'execucao remota de codigo no cliente/servidor'
            ))

        # 2. Luraph/obfuscador fora de scripts pagos
        if LUA_OBFUSCATED_MARKER.search(content):
            if not self.is_trusted_obfuscated_path(file_path):
                findings.append((
                    'LUA_OBFUSCATED',
                    'Arquivo Lua obfuscado (Luraph/Prometheus) fora de '
                    'pasta de script pago — verificar manualmente'
                ))

        return findings

    # ------------------------------------------------------------------
    # Detecção de fxmanifest.lua infectado
    # ------------------------------------------------------------------

    def find_malicious_manifest_blocks(self, file_path):
        """
        Retorna lista de blocos injetados no manifest, ou lista vazia.
        Só flagra blocos que contenham pelo menos um JS confirmado como malicioso.
        """
        if file_path.name.lower() != 'fxmanifest.lua':
            return []

        content = self.read_file(file_path)
        if content is None:
            return []

        found = []

        # Padrão atual: shared_scripts/server_scripts com .js
        for match in MANIFEST_INJECT_PATTERN.finditer(content):
            block = match.group(0)
            # Verifica se pelo menos um JS no bloco é malicioso
            js_refs = re.findall(r"['\"]([^'\"]+\.js)['\"]", block)
            for js_rel in js_refs:
                js_abs = file_path.parent / js_rel
                if self.is_malicious_js(js_abs):
                    found.append(block)
                    break

        # Padrão legado: --[[server.lua]] com .js
        for match in MANIFEST_LEGACY_PATTERN.finditer(content):
            found.append(match.group(0))

        return found

    # ------------------------------------------------------------------
    # Limpeza de fxmanifest.lua
    # ------------------------------------------------------------------

    def clean_manifest(self, file_path, dry_run=False):
        """
        Limpeza cirúrgica de fxmanifest.lua:
        - Se o bloco contém APENAS .js maliciosos -> remove o bloco inteiro
        - Se o bloco é misto (dll, glob + .js malicioso) -> remove só as linhas .js
        Retorna (blocos_modificados, arquivos_js_deletados).
        """
        content = self.read_file(file_path)
        if content is None:
            return 0, 0

        removed_js_files = []
        modifications = [0]

        def process_block(match):
            block_text = match.group(0)

            inner_match = re.search(r'\{(.*?)\}', block_text, re.DOTALL)
            if not inner_match:
                return block_text

            inner = inner_match.group(1)
            lines = inner.split('\n')

            new_lines = []
            js_lines_removed = 0

            for line in lines:
                js_ref = re.search(r"['\"]([^'\"]+\.js)['\"]", line)
                if js_ref:
                    js_rel = js_ref.group(1)
                    js_abs = file_path.parent / js_rel
                    is_bad = (
                        any(p.resolve() == js_abs.resolve() for p in self.malicious_files)
                        or self.is_malicious_js(js_abs)
                    )
                    if is_bad:
                        removed_js_files.append(js_abs)
                        js_lines_removed += 1
                        continue  # remove a linha
                new_lines.append(line)

            if js_lines_removed == 0:
                return block_text

            modifications[0] += 1

            # Verificar se sobrou alguma entrada útil
            useful = [
                l for l in new_lines
                if l.strip()
                and not re.match(r'\s*(shared_scripts|server_scripts)\s*\{?\s*$', l)
                and l.strip() != '}'
                and l.strip() != '{'
            ]

            if not useful:
                if dry_run:
                    print(f"   [DRY-RUN] Removeria bloco completo")
                return ''
            else:
                # Bloco misto: reconstrói sem as linhas JS maliciosas
                # Substituir apenas o conteúdo interno, mantendo "keyword { ... }"
                new_inner = '\n'.join(new_lines)
                # Limpar vírgula pendente antes do fechamento }
                new_inner = re.sub(r',(\s*\n\s*\})', r'\1', new_inner)
                new_block = block_text[:inner_match.start(1)] + new_inner + block_text[inner_match.end(1):]
                if dry_run:
                    print(f"   [DRY-RUN] Removeria linha(s) JS (mantendo entradas legítimas)")
                return new_block

        new_content = MANIFEST_INJECT_PATTERN.sub(process_block, content)

        # Padrão legado
        def remove_legacy(match):
            modifications[0] += 1
            return ''
        new_content = MANIFEST_LEGACY_PATTERN.sub(remove_legacy, new_content)

        # Remover comentários do ColdGG Dumper
        new_content = re.sub(
            r'\n-- .{0,5}Dump realizado com o ColdGG Dumper!.*?(?=\n\n|\Z)',
            '',
            new_content,
            flags=re.DOTALL
        )
        new_content = re.sub(r'\n-- .{0,5}Discord ColdGG:[^\n]*', '', new_content)
        new_content = re.sub(r'\n-- .{0,5}Convite permanente:[^\n]*', '', new_content)

        new_content = new_content.rstrip() + '\n'

        if dry_run:
            print(f"   [DRY-RUN] {modifications[0]} modificação(ões) em {file_path.name}")
            for js in removed_js_files:
                print(f"             -> Deletaria JS: {js}")
            return modifications[0], 0

        # Salvar manifest limpo
        if modifications[0] > 0:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            except Exception as e:
                print(f"   ERRO ao salvar {file_path}: {e}")
                return 0, 0

        # Deletar arquivos JS maliciosos referenciados
        deleted_js = 0
        for js_path in removed_js_files:
            if not js_path.exists():
                continue
            try:
                js_path.unlink()
                print(f"   JS deletado: {js_path}")
                deleted_js += 1
            except Exception:
                try:
                    import subprocess
                    subprocess.run(['del', '/F', '/Q', str(js_path)],
                                   shell=True, capture_output=True)
                    if not js_path.exists():
                        print(f"   JS deletado (cmd): {js_path}")
                        deleted_js += 1
                    else:
                        print(f"   ERRO: nao foi possivel deletar {js_path}")
                except Exception as e2:
                    print(f"   ERRO ao deletar {js_path}: {e2}")

        return modifications[0], deleted_js

    # ------------------------------------------------------------------
    # Varredura principal
    # ------------------------------------------------------------------

    def scan_directory(self, directory=None):
        if directory is None:
            directory = self.root_path
        directory = Path(directory)

        if not directory.exists():
            print(f"Diretório não existe: {directory}")
            return

        if self.should_ignore(directory):
            return

        try:
            for item in sorted(directory.iterdir()):
                if self.should_ignore(item):
                    continue

                if item.is_dir():
                    self.scanned_dirs += 1
                    self.scan_directory(item)

                elif item.is_file():
                    self.scanned_files += 1
                    ext = item.suffix.lower()

                    if ext == '.js' and self.is_malicious_js(item):
                        self.malicious_files.append(item)
                        print(f"[JS MALICIOSO] {item}")

                    elif ext == '.lua':
                        blocks = self.find_malicious_manifest_blocks(item)
                        if blocks:
                            self.malicious_manifests.append((item, blocks))
                            print(f"[MANIFEST INFECTADO] {item} ({len(blocks)} bloco(s))")

                        lua_findings = self.check_lua_backdoor(item)
                        for tipo, descricao in lua_findings:
                            self.suspicious_lua.append((item, tipo, descricao))
                            print(f"[{tipo}] {item}")

        except PermissionError:
            print(f"Sem permissão: {directory}")
        except Exception as e:
            print(f"Erro em {directory}: {e}")

    # ------------------------------------------------------------------
    # Limpeza em massa
    # ------------------------------------------------------------------

    def run_cleanup(self, dry_run=False):
        """
        Remove arquivos JS maliciosos standalone e limpa manifests infectados.
        Arquivos JS referenciados pelos manifests são deletados durante a limpeza dos manifests.
        """
        total_js_deleted = 0
        total_blocks_removed = 0

        # 1. Limpar manifests (e deletar JS referenciados)
        if self.malicious_manifests:
            print(f"\n--- Limpando {len(self.malicious_manifests)} fxmanifest.lua infectado(s) ---")
            cleaned_manifest_js = set()

            for file_path, blocks in self.malicious_manifests:
                print(f"\n  Manifest: {file_path}")
                blocks_removed, js_deleted = self.clean_manifest(file_path, dry_run)
                total_blocks_removed += blocks_removed
                total_js_deleted += js_deleted

                # Rastrear JS removidos por manifests para não deletar duplicado
                for block in blocks:
                    for js_ref in re.findall(r"['\"]([^'\"]+\.js)['\"]", block):
                        cleaned_manifest_js.add((file_path.parent / js_ref).resolve())

        # 2. Deletar arquivos JS maliciosos standalone (não referenciados por manifest)
        standalone = [
            f for f in self.malicious_files
            if f.resolve() not in {
                (file_path.parent / js_ref).resolve()
                for file_path, blocks in self.malicious_manifests
                for block in blocks
                for js_ref in re.findall(r"['\"]([^'\"]+\.js)['\"]", block)
            }
        ]

        if standalone:
            print(f"\n--- Deletando {len(standalone)} JS malicioso(s) standalone ---")
            for js_path in standalone:
                if dry_run:
                    print(f"   [DRY-RUN] Deletaria: {js_path}")
                else:
                    try:
                        js_path.unlink()
                        print(f"   ✅ Deletado: {js_path}")
                        total_js_deleted += 1
                    except Exception as e:
                        print(f"   ERRO: {js_path}: {e}")

        return total_blocks_removed, total_js_deleted

    # ------------------------------------------------------------------
    # Relatório
    # ------------------------------------------------------------------

    def generate_report(self):
        lines = []
        sep = "=" * 80
        tudo_limpo = (
            not self.malicious_files
            and not self.malicious_manifests
            and not self.suspicious_lua
        )
        lines += [
            sep,
            "RELATORIO DE VARREDURA - SCANNER DE BACKDOOR",
            sep,
            f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            f"Diretorio escaneado: {self.root_path}",
            f"Arquivos escaneados: {self.scanned_files}",
            f"Diretorios escaneados: {self.scanned_dirs}",
            f"Arquivos JS maliciosos: {len(self.malicious_files)}",
            f"fxmanifest.lua infectados: {len(self.malicious_manifests)}",
            f"Lua suspeitos (RCE/obfuscado): {len(self.suspicious_lua)}",
            "",
        ]

        if self.malicious_files:
            lines.append("ARQUIVOS JS MALICIOSOS (deletar):")
            lines.append("-" * 80)
            for i, p in enumerate(self.malicious_files, 1):
                lines.append(f"  {i}. {p}")
            lines.append("")

        if self.malicious_manifests:
            lines.append("fxmanifest.lua INFECTADOS (limpar):")
            lines.append("-" * 80)
            for i, (p, blocks) in enumerate(self.malicious_manifests, 1):
                lines.append(f"  {i}. {p}")
                for b in blocks:
                    preview = b.replace('\n', ' ')[:100]
                    lines.append(f"     Bloco: {preview}...")
            lines.append("")

        if self.suspicious_lua:
            lines.append("LUA SUSPEITO (verificar manualmente):")
            lines.append("-" * 80)
            for i, (p, tipo, descricao) in enumerate(self.suspicious_lua, 1):
                lines.append(f"  {i}. [{tipo}] {p}")
                lines.append(f"     {descricao}")
            lines.append("")

        if tudo_limpo:
            lines.append("NENHUM ARQUIVO MALICIOSO ENCONTRADO!")
            lines.append("")

        lines.append(sep)
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def find_server_root(start_path):
    """
    Sobe na árvore de diretórios procurando a raiz do servidor FiveM.
    Marcadores: server.cfg + resources/ (ideal), ou resources/ sozinha.
    Funciona independente de onde o scanner foi colocado.
    """
    path = Path(start_path).resolve()

    best = None
    for _ in range(8):  # sobe até 8 níveis
        if (path / 'resources').is_dir():
            best = path  # salva o candidato mais alto encontrado
        parent = path.parent
        if parent == path:
            break
        path = parent

    if best:
        # Prefere o candidato que também tem server.cfg
        check = best
        for _ in range(8):
            if (check / 'server.cfg').exists() and (check / 'resources').is_dir():
                return check
            parent = check.parent
            if parent == check:
                break
            check = parent
        return best

    return Path(start_path).resolve()


def main():
    print("=" * 80)
    print("SCANNER DE BACKDOOR - Deteccao e Remocao de Codigo Malicioso")
    print("=" * 80)

    # Determinar raiz: argumento CLI > auto-detecção a partir do script
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        root_path = Path(sys.argv[1]).resolve()
    else:
        script_dir = Path(os.path.abspath(__file__)).parent
        root_path = find_server_root(script_dir)

    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    auto_clean = '--auto' in sys.argv

    if dry_run:
        print("MODO DRY-RUN - nenhum arquivo sera alterado")
    print(f"\nRaiz detectada: {root_path}\n")

    scanner = BackdoorScanner(root_path)
    scanner.scan_directory()

    report = scanner.generate_report()
    print("\n" + report)

    # Salvar relatório
    report_path = Path(root_path) / f"relatorio_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Relatório salvo em: {report_path}")
    except Exception as e:
        print(f"Aviso: não foi possível salvar relatório: {e}")

    nada = (
        not scanner.malicious_files
        and not scanner.malicious_manifests
        and not scanner.suspicious_lua
    )
    if nada:
        print("\nSistema limpo.")
        return

    if scanner.suspicious_lua and not scanner.malicious_files and not scanner.malicious_manifests:
        print("\nNenhum arquivo para limpeza automatica.")
        print("Verifique os itens [LUA_RCE] e [LUA_OBFUSCATED] no relatorio manualmente.")
        return

    # Confirmação de limpeza
    if not dry_run:
        if auto_clean:
            resposta = 's'
        else:
            print()
            resposta = input("❓ Deseja executar a limpeza agora? (s/N): ").strip().lower()

        if resposta in ('s', 'sim', 'y', 'yes'):
            blocks_removed, js_deleted = scanner.run_cleanup(dry_run=False)
            print(f"\n✅ Blocos de manifest removidos: {blocks_removed}")
            print(f"✅ Arquivos JS deletados: {js_deleted}")
        else:
            print("Limpeza cancelada.")
    else:
        scanner.run_cleanup(dry_run=True)

    print("\n" + "=" * 80)
    print("✅ Varredura concluída!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelado pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
