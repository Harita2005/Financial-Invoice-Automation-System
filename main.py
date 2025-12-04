#!/usr/bin/env python3
"""
Invoice Generator System - Main Entry Point
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point - choose between CLI and GUI"""
    if len(sys.argv) > 1:
        # CLI mode
        from src.cli import cli
        cli()
    else:
        # GUI mode
        try:
            from src.gui import main as gui_main
            gui_main()
        except ImportError as e:
            print(f"GUI not available: {e}")
            print("Use CLI mode instead: python main.py --help")

if __name__ == '__main__':
    main()