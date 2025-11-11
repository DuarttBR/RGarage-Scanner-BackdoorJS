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

# Padrões maliciosos para detectar
MALICIOUS_PATTERNS = [
    # Padrão 1: x=(e,k=3)=>[...e].map(c=>String.fromCharCode(c.charCodeAt()^k))
    r'x=\(e,k=3\)=>\[\.\.\.e\]\.map\(c=>String\.fromCharCode\(c\.charCodeAt\(\)\^k\)\)',
    # Padrão 2: x=s=>eval(s.replace(/\\u([0-9a-f]{4})/g,(_,h)=>String.fromCharCode(parseInt(h,16))).split('').map(c=>String.fromCharCode(c.charCodeAt(0)^3))
    r'x=s=>eval\(s\.replace\(/\\\\u\(\[0-9a-f\]\{4\}\)/g',
    # Padrão 3: globalThis[x("fubo")]
    r'globalThis\[x\("fubo"\)\]',
    # Padrão 4: Comentário suspeito /* [ nome_recurso ] */
    r'/\*\s*\[\s*[^\]]+\s*\]\s*\*/.*x=\(e,k=3\)',
    r'/\*\s*\[\s*[^\]]+\s*\]\s*\*/.*x=s=>eval',
]

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

# Nomes de arquivos suspeitos (tentam se passar por arquivos legítimos do Git)
SUSPICIOUS_FILENAMES = [
    'gitignore.js',
    '.gitignore.js',
    'gitattributes.js',
    '.gitattributes.js',
    'gitconfig.js',
    '.gitconfig.js',
    'gitkeep.js',
    '.gitkeep.js',
    'gitmodules.js',
    '.gitmodules.js',
    'githooks.js',
    '.githooks.js',
]

# Tamanho máximo de arquivo para verificar (em bytes)
MAX_FILE_SIZE = 50000  # 50KB

class BackdoorScanner:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.malicious_files = []
        self.malicious_lines = []  # Arquivos com linhas maliciosas para limpar
        self.scanned_files = 0
        self.scanned_dirs = 0
        
    def should_ignore(self, path):
        """Verifica se o caminho deve ser ignorado"""
        path_str = str(path)
        for ignore in IGNORE_PATHS:
            if ignore in path_str:
                return True
        return False
    
    def is_suspicious_filename(self, file_path):
        """Verifica se o nome do arquivo é suspeito (tenta se passar por arquivo legítimo)"""
        filename_lower = file_path.name.lower()
        for suspicious in SUSPICIOUS_FILENAMES:
            if suspicious.lower() in filename_lower or filename_lower == suspicious.lower():
                return True
        return False
    
    def is_malicious_file(self, file_path):
        """Verifica se um arquivo contém código malicioso"""
        try:
            # Verifica se o nome do arquivo é suspeito (ex: gitignore.js)
            if self.is_suspicious_filename(file_path):
                return True
            
            # Verifica se é arquivo oculto (começa com ponto)
            if file_path.name.startswith('.'):
                # Verifica tamanho
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    return False
                
                # Lê o conteúdo do arquivo
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(MAX_FILE_SIZE)  # Lê apenas os primeiros bytes
                        
                        # Verifica padrões maliciosos
                        for pattern in MALICIOUS_PATTERNS:
                            if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                                return True
                except Exception as e:
                    # Se não conseguir ler, verifica pelo nome
                    suspicious_names = ['.eventhandler', '.snapshot', '.dummydata', '.rollup.config', 
                                       '.env', '.tsup.config', '.webpack.config', 'gitignore', 
                                       'gitattributes', 'gitconfig']
                    if any(name in file_path.name.lower() for name in suspicious_names):
                        return True
                    return False
            
            # Verifica arquivos normais também
            if file_path.stat().st_size > MAX_FILE_SIZE:
                return False
                
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(MAX_FILE_SIZE)
                    
                    # Verifica padrões maliciosos
                    for pattern in MALICIOUS_PATTERNS:
                        if re.search(pattern, content, re.IGNORECASE | re.DOTALL):
                            return True
            except:
                return False
                
        except Exception as e:
            return False
            
        return False
    
    def has_malicious_manifest_line(self, file_path):
        """Verifica se um arquivo fxmanifest.lua contém linhas maliciosas
        Retorna: False se não encontrar, ou (True, line_num, line_content) se encontrar
        """
        if file_path.name.lower() != 'fxmanifest.lua':
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            # Padrão: --[[server.lua]] seguido de muitos espaços e depois um arquivo .js
            # Regex: --\[\[server\.lua\]\]\s+['"].*\.js['"]
            pattern = r'--\[\[server\.lua\]\]\s+[\'"](.*\.js)[\'"]'
            
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    return (True, line_num, line.strip())
                    
        except Exception as e:
            return False
        
        return False
    
    def clean_manifest_file(self, file_path, dry_run=False):
        """Remove linhas maliciosas de um arquivo fxmanifest.lua"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            pattern = r'--\[\[server\.lua\]\]\s+[\'"](.*\.js)[\'"]'
            cleaned_lines = []
            removed_count = 0
            
            for line in lines:
                if re.search(pattern, line):
                    if not dry_run:
                        removed_count += 1
                    else:
                        print(f"   [SIMULAÇÃO] Removeria linha: {line.strip()[:80]}...")
                    continue
                cleaned_lines.append(line)
            
            if removed_count > 0 and not dry_run:
                with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                    f.writelines(cleaned_lines)
                return removed_count
            
            return 0
        except Exception as e:
            print(f"   ❌ ERRO ao limpar {file_path}: {e}")
            return 0
    
    def scan_directory(self, directory=None):
        """Escaneia um diretório recursivamente"""
        if directory is None:
            directory = self.root_path
            
        directory = Path(directory)
        
        if not directory.exists():
            print(f"❌ Diretório não existe: {directory}")
            return
        
        if self.should_ignore(directory):
            return
        
        try:
            for item in directory.iterdir():
                if self.should_ignore(item):
                    continue
                
                if item.is_dir():
                    self.scanned_dirs += 1
                    self.scan_directory(item)
                elif item.is_file():
                    self.scanned_files += 1
                    if item.suffix.lower() in CHECK_EXTENSIONS:
                        # Verifica arquivos JavaScript maliciosos
                        if item.suffix.lower() == '.js' and self.is_malicious_file(item):
                            self.malicious_files.append(item)
                            # Indica o motivo da detecção
                            if self.is_suspicious_filename(item):
                                print(f"🔴 MALICIOSO ENCONTRADO (nome suspeito): {item}")
                            else:
                                print(f"🔴 MALICIOSO ENCONTRADO: {item}")
                        # Verifica arquivos fxmanifest.lua com linhas maliciosas
                        elif item.suffix.lower() == '.lua':
                            result = self.has_malicious_manifest_line(item)
                            if result:
                                if isinstance(result, tuple):
                                    _, line_num, line_content = result
                                    self.malicious_lines.append((item, line_num, line_content))
                                    print(f"🔴 LINHA MALICIOSA ENCONTRADA em {item} (linha {line_num})")
                                else:
                                    self.malicious_lines.append((item, 0, ""))
                                    print(f"🔴 LINHA MALICIOSA ENCONTRADA em {item}")
        except PermissionError:
            print(f"⚠️  Sem permissão para acessar: {directory}")
        except Exception as e:
            print(f"⚠️  Erro ao escanear {directory}: {e}")
    
    def clean_malicious_manifest_lines(self, dry_run=False):
        """Remove linhas maliciosas de arquivos fxmanifest.lua"""
        cleaned = 0
        failed = 0
        
        if not self.malicious_lines:
            return cleaned, failed
        
        print(f"\n📋 Total de arquivos fxmanifest.lua com linhas maliciosas: {len(self.malicious_lines)}")
        
        if dry_run:
            print("\n🔍 MODO DRY-RUN (simulação) - Nenhuma linha será removida")
        
        for file_path, line_num, line_content in self.malicious_lines:
            try:
                removed = self.clean_manifest_file(file_path, dry_run)
                if removed > 0:
                    print(f"   ✅ LIMPO: {file_path} ({removed} linha(s) removida(s))")
                    cleaned += removed
                elif dry_run:
                    print(f"   [SIMULAÇÃO] Limparia: {file_path}")
            except Exception as e:
                print(f"   ❌ ERRO ao limpar {file_path}: {e}")
                failed += 1
        
        return cleaned, failed
    
    def delete_malicious_files(self, dry_run=False):
        """Deleta arquivos maliciosos encontrados"""
        deleted = 0
        failed = 0
        
        if not self.malicious_files and not self.malicious_lines:
            print("\n✅ Nenhum arquivo malicioso encontrado!")
            return deleted, failed
        
        print(f"\n📋 Total de arquivos maliciosos encontrados: {len(self.malicious_files)}")
        
        if dry_run:
            print("\n🔍 MODO DRY-RUN (simulação) - Nenhum arquivo será deletado")
        
        for file_path in self.malicious_files:
            try:
                if dry_run:
                    print(f"   [SIMULAÇÃO] Deletaria: {file_path}")
                else:
                    # Tenta deletar usando diferentes métodos
                    try:
                        os.remove(str(file_path))
                        print(f"   ✅ DELETADO: {file_path}")
                        deleted += 1
                    except PermissionError:
                        # Tenta com método alternativo
                        try:
                            import subprocess
                            if sys.platform == 'win32':
                                subprocess.run(['del', '/F', '/Q', str(file_path)], 
                                             shell=True, capture_output=True)
                                if not file_path.exists():
                                    print(f"   ✅ DELETADO (cmd): {file_path}")
                                    deleted += 1
                                else:
                                    raise Exception("Falha ao deletar")
                            else:
                                os.unlink(str(file_path))
                                print(f"   ✅ DELETADO: {file_path}")
                                deleted += 1
                        except Exception as e2:
                            print(f"   ❌ FALHA ao deletar {file_path}: {e2}")
                            failed += 1
            except Exception as e:
                print(f"   ❌ ERRO ao processar {file_path}: {e}")
                failed += 1
        
        return deleted, failed
    
    def generate_report(self):
        """Gera relatório da varredura"""
        report = []
        report.append("=" * 80)
        report.append("RELATÓRIO DE VARREdura - SCANNER DE BACKDOOR")
        report.append("=" * 80)
        report.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append(f"Diretório escaneado: {self.root_path}")
        report.append(f"Arquivos escaneados: {self.scanned_files}")
        report.append(f"Diretórios escaneados: {self.scanned_dirs}")
        report.append(f"Arquivos JavaScript maliciosos encontrados: {len(self.malicious_files)}")
        report.append(f"Arquivos fxmanifest.lua com linhas maliciosas: {len(self.malicious_lines)}")
        report.append("")
        
        if self.malicious_files:
            report.append("ARQUIVOS JAVASCRIPT MALICIOSOS ENCONTRADOS:")
            report.append("-" * 80)
            for i, file_path in enumerate(self.malicious_files, 1):
                report.append(f"{i}. {file_path}")
            report.append("")
        
        if self.malicious_lines:
            report.append("ARQUIVOS FXMANIFEST.LUA COM LINHAS MALICIOSAS:")
            report.append("-" * 80)
            for i, (file_path, line_num, line_content) in enumerate(self.malicious_lines, 1):
                report.append(f"{i}. {file_path} (linha {line_num})")
                if line_content:
                    report.append(f"   Conteúdo: {line_content[:100]}...")
            report.append("")
        
        if not self.malicious_files and not self.malicious_lines:
            report.append("✅ NENHUM ARQUIVO MALICIOSO ENCONTRADO!")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    print("=" * 80)
    print("🔍 SCANNER DE BACKDOOR - Detecção e Remoção de Código Malicioso")
    print("=" * 80)
    print()
    print(" " * 20 + "╔═══════════════════════════════════╗")
    print(" " * 20 + "║   🏍️  Desenvolvido por          ║")
    print(" " * 20 + "║      RYU GARAGE                  ║")
    print(" " * 20 + "║                                  ║")
    print(" " * 20 + "║   Proteção e Segurança           ║")
    print(" " * 20 + "║   para Servidores FiveM          ║")
    print(" " * 20 + "╚═══════════════════════════════════╝")
    print()
    print(" " * 25 + "Desenvolvido com ❤️")
    print()
    print("=" * 80)
    print()
    
    # Determina o diretório raiz
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        # Usa o diretório atual
        root_path = os.getcwd()
    
    # Verifica modo dry-run
    dry_run = '--dry-run' in sys.argv or '-n' in sys.argv
    
    if dry_run:
        print("⚠️  MODO DRY-RUN ATIVADO - Nenhum arquivo será deletado")
        print()
    
    print(f"📁 Escaneando diretório: {root_path}")
    print()
    
    # Cria scanner
    scanner = BackdoorScanner(root_path)
    
    # Escaneia
    print("🔍 Iniciando varredura...")
    scanner.scan_directory()
    
    # Gera relatório
    report = scanner.generate_report()
    print(report)
    
    # Salva relatório
    report_file = Path(root_path) / f"relatorio_scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Relatório salvo em: {report_file}")
    except Exception as e:
        print(f"⚠️  Não foi possível salvar o relatório: {e}")
    
    # Limpa linhas maliciosas de fxmanifest.lua
    if scanner.malicious_lines:
        print()
        if not dry_run:
            response = input("❓ Deseja remover as linhas maliciosas dos arquivos fxmanifest.lua? (s/N): ").strip().lower()
            if response in ['s', 'sim', 'y', 'yes']:
                cleaned, failed = scanner.clean_malicious_manifest_lines(dry_run=False)
                print()
                print(f"✅ Linhas removidas: {cleaned}")
                if failed > 0:
                    print(f"❌ Falhas ao limpar: {failed}")
            else:
                print("❌ Operação cancelada pelo usuário")
        else:
            scanner.clean_malicious_manifest_lines(dry_run=True)
    
    # Deleta arquivos maliciosos
    if scanner.malicious_files:
        print()
        if not dry_run:
            response = input("❓ Deseja deletar os arquivos maliciosos? (s/N): ").strip().lower()
            if response in ['s', 'sim', 'y', 'yes']:
                deleted, failed = scanner.delete_malicious_files(dry_run=False)
                print()
                print(f"✅ Arquivos deletados: {deleted}")
                if failed > 0:
                    print(f"❌ Falhas ao deletar: {failed}")
            else:
                print("❌ Operação cancelada pelo usuário")
        else:
            scanner.delete_malicious_files(dry_run=True)
    
    if not scanner.malicious_files and not scanner.malicious_lines:
        print()
        print("✅ Nenhum arquivo malicioso encontrado! Sistema limpo.")
    
    print()
    print("=" * 80)
    print("✅ Varredura concluída!")
    print("=" * 80)
    print()
    print(" " * 20 + "╔═══════════════════════════════════╗")
    print(" " * 20 + "║   🏍️  RYU GARAGE                 ║")
    print(" " * 20 + "║   Desenvolvido com ❤️            ║")
    print(" " * 20 + "╚═══════════════════════════════════╝")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

