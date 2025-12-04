#!/usr/bin/env python3
"""
Launch Best UI Invoice Generator
"""

import subprocess
import sys
import os
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open browser after delay"""
    webbrowser.open('http://localhost:5000')

def main():
    print("🚀 LAUNCHING BEST UI INVOICE GENERATOR")
    print("=" * 50)
    
    # Check Flask
    try:
        import flask
        print("✅ Flask ready")
    except ImportError:
        print("📦 Installing Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask"])
        print("✅ Flask installed")
    
    # Create directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    print("✅ System ready")
    print("\n🌟 BEST UI FEATURES:")
    print("   • Modern gradient design")
    print("   • Animated elements")
    print("   • Real-time calculations")
    print("   • Professional styling")
    print("   • Mobile responsive")
    print("   • Smooth transitions")
    print("   • Beautiful icons")
    print("   • Glass morphism effects")
    
    print(f"\n🌐 Opening at: http://localhost:5000")
    print("📱 Mobile access: http://YOUR_IP:5000")
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    try:
        from best_ui_app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Best UI Invoice Generator stopped!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    main()