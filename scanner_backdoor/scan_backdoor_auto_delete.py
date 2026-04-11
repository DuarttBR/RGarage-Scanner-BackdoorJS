#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scanner de Backdoor - Modo Automatico
Alias para: python scan_backdoor.py --auto
Mantido para compatibilidade com versoes anteriores.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Injeta --auto nos argumentos e delega ao script principal
if '--auto' not in sys.argv:
    sys.argv.append('--auto')

from scan_backdoor import main
main()
