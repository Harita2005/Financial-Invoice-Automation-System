#!/usr/bin/env python3
"""
Setup script for Invoice Generator System
"""

import os
import sys
import json
from pathlib import Path

def create_directories():
    """Create necessary directories"""
    directories = [
        'output',
        'output/preview', 
        'logs',
        'templates',
        'data'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = {
        'reportlab': 'reportlab',
        'pymongo': 'pymongo', 
        'mysql-connector-python': 'mysql.connector',
        'Pillow': 'PIL',
        'python-dateutil': 'dateutil',
        'pydantic': 'pydantic',
        'click': 'click'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall missing packages with:")
        print("pip install -r requirements.txt")
        return False
    else:
        print("All required packages are installed")
        return True

def validate_config():
    """Validate configuration file"""
    config_path = 'config/settings.json'
    
    if not os.path.exists(config_path):
        print(f"Configuration file not found: {config_path}")
        return False
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Check required sections
        required_sections = ['company', 'invoice', 'database', 'output']
        for section in required_sections:
            if section not in config:
                print(f"Missing configuration section: {section}")
                return False
        
        print("Configuration file is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in configuration file: {e}")
        return False

def create_sample_logo():
    """Create a simple sample logo placeholder"""
    logo_path = 'templates/logo.png'
    
    if os.path.exists(logo_path):
        print(f"Logo file already exists: {logo_path}")
        return
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a simple logo placeholder
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple rectangle and text
        draw.rectangle([10, 10, 190, 90], outline='navy', width=3)
        
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        # Add company name text
        text = "YOUR LOGO"
        if font:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        else:
            text_width, text_height = 80, 20
        
        x = (200 - text_width) // 2
        y = (100 - text_height) // 2
        
        draw.text((x, y), text, fill='navy', font=font)
        
        img.save(logo_path)
        print(f"Created sample logo: {logo_path}")
        
    except ImportError:
        # If PIL is not available, create a text placeholder
        with open(logo_path.replace('.png', '.txt'), 'w') as f:
            f.write("Replace this file with your company logo (PNG format)")
        print(f"Created logo placeholder: {logo_path.replace('.png', '.txt')}")

def main():
    """Main setup function"""
    print("Setting up Invoice Generator System...")
    print("=" * 50)
    
    # Create directories
    print("\nCreating directories...")
    create_directories()
    
    # Check dependencies
    print("\nChecking dependencies...")
    deps_ok = check_dependencies()
    
    # Validate configuration
    print("\nValidating configuration...")
    config_ok = validate_config()
    
    # Create sample logo
    print("\nSetting up logo...")
    create_sample_logo()
    
    print("\n" + "=" * 50)
    
    if deps_ok and config_ok:
        print("Setup completed successfully!")
        print("\nNext steps:")
        print("1. Update config/settings.json with your company details")
        print("2. Replace templates/logo.png with your company logo")
        print("3. Set up your database (MySQL or MongoDB)")
        print("4. Run: python create_sample_invoice.py")
        print("5. Start using: python main.py")
    else:
        print("Setup completed with issues")
        print("Please resolve the issues above before using the system")
    
    return 0 if (deps_ok and config_ok) else 1

if __name__ == '__main__':
    sys.exit(main())