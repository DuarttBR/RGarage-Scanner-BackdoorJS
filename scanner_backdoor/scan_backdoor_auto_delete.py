#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner de Backdoor - Modo Automático (Deleta sem perguntar)
"""

import sys
import os

# Adiciona o diretório atual ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa e executa o scanner principal
from scan_backdoor import BackdoorScanner
from pathlib import Path
from datetime import datetime

def main():
    print("=" * 80)
    print("🔍 SCANNER DE BACKDOOR - Modo Automático")
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
    print("⚠️  ATENÇÃO: Este modo deletará automaticamente todos os arquivos maliciosos!")
    print()
    print("=" * 80)
    print()
    
    # Determina o diretório raiz
    if len(sys.argv) > 1:
        root_path = sys.argv[1]
    else:
        root_path = os.getcwd()
    
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
    
    # Limpa linhas maliciosas de fxmanifest.lua automaticamente
    if scanner.malicious_lines:
        print()
        print("🧹 Removendo linhas maliciosas dos arquivos fxmanifest.lua automaticamente...")
        cleaned, failed = scanner.clean_malicious_manifest_lines(dry_run=False)
        print()
        print(f"✅ Linhas removidas: {cleaned}")
        if failed > 0:
            print(f"❌ Falhas ao limpar: {failed}")
    
    # Deleta arquivos maliciosos automaticamente
    if scanner.malicious_files:
        print()
        print("🗑️  Deletando arquivos maliciosos automaticamente...")
        deleted, failed = scanner.delete_malicious_files(dry_run=False)
        print()
        print(f"✅ Arquivos deletados: {deleted}")
        if failed > 0:
            print(f"❌ Falhas ao deletar: {failed}")
    
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

