#!/usr/bin/env python3
"""
Create a simple logo for the invoice generator
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_simple_logo():
    """Create a simple company logo"""
    
    # Create image
    width, height = 200, 100
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([5, 5, width-5, height-5], outline='#1f4e79', width=3)
    
    # Add company text
    try:
        # Try to use a better font if available
        font_large = ImageFont.truetype("arial.ttf", 16)
        font_small = ImageFont.truetype("arial.ttf", 10)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Main company name
    company_text = "YOUR COMPANY"
    bbox = draw.textbbox((0, 0), company_text, font=font_large)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = 25
    draw.text((x, y), company_text, fill='#1f4e79', font=font_large)
    
    # Subtitle
    subtitle = "Professional Services"
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = 55
    draw.text((x, y), subtitle, fill='#666666', font=font_small)
    
    # Save logo
    logo_path = 'templates/logo.png'
    img.save(logo_path)
    print(f"Logo created: {logo_path}")

if __name__ == '__main__':
    create_simple_logo()