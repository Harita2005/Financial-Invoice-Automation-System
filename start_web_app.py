#!/usr/bin/env python3
"""
Start the Web Invoice Generator
"""

import subprocess
import sys
import os
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open browser after a delay"""
    webbrowser.open('http://localhost:5000')

def main():
    print("🚀 Starting Invoice Generator Web Application...")
    print("=" * 50)
    
    # Check if Flask is installed
    try:
        import flask
        print("✅ Flask is installed")
    except ImportError:
        print("❌ Flask not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask==2.3.3"])
        print("✅ Flask installed successfully")
    
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('output', exist_ok=True)
    
    print("✅ Directories created")
    print("✅ Starting web server...")
    print("\n🌐 Your Invoice Generator will open at: http://localhost:5000")
    print("📱 Access from mobile: http://YOUR_IP:5000")
    print("\n⚡ Features Available:")
    print("   • Modern responsive UI")
    print("   • Real-time GST calculations") 
    print("   • Multiple items support")
    print("   • Downloadable PDF invoices")
    print("   • Indian Rupee currency")
    print("   • Professional invoice templates")
    
    # Open browser after 2 seconds
    Timer(2.0, open_browser).start()
    
    # Start the Flask app
    try:
        from web_invoice_app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\n👋 Invoice Generator stopped. Thank you!")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("Please check if all files are in place and try again.")

if __name__ == '__main__':
    main()