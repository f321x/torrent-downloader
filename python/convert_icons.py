#!/usr/bin/env python3
import os
import sys
import cairosvg
from PIL import Image

def convert_svg_to_png(svg_path, output_path, size):
    """Convert SVG to PNG at specified size."""
    cairosvg.svg2png(url=svg_path, write_to=output_path, output_width=size, output_height=size)

def convert_svg_to_ico(svg_path, ico_path, sizes=[16, 32, 48, 64, 128, 256]):
    """Convert SVG to ICO with multiple sizes."""
    temp_dir = 'temp_icons'
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Convert SVG to multiple PNG files of different sizes
        png_files = []
        for size in sizes:
            png_path = os.path.join(temp_dir, f'icon_{size}.png')
            convert_svg_to_png(svg_path, png_path, size)
            png_files.append(Image.open(png_path))
        
        # Convert to ICO
        png_files[0].save(
            ico_path,
            format='ICO',
            sizes=[(size, size) for size in sizes],
            append_images=png_files[1:]
        )
        
    finally:
        # Clean up
        for size in sizes:
            try:
                os.remove(os.path.join(temp_dir, f'icon_{size}.png'))
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

def convert_svg_to_icns(svg_path, icns_path):
    """Convert SVG to ICNS with required macOS icon sizes."""
    sizes = [16, 32, 64, 128, 256, 512, 1024]
    temp_dir = 'temp_icons'
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Convert SVG to PNG files of different sizes
        for size in sizes:
            # Regular and @2x versions (except for 1024)
            if size != 1024:
                png_path_2x = os.path.join(temp_dir, f'icon_{size}x{size}@2x.png')
                convert_svg_to_png(svg_path, png_path_2x, size*2)
            
            png_path = os.path.join(temp_dir, f'icon_{size}x{size}.png')
            convert_svg_to_png(svg_path, png_path, size)
        
        # Create iconset directory
        iconset_dir = os.path.join(temp_dir, 'icon.iconset')
        os.makedirs(iconset_dir, exist_ok=True)
        
        # Organize files according to macOS naming convention
        for size in sizes:
            if size == 1024:
                src = os.path.join(temp_dir, f'icon_{size}x{size}.png')
                dst = os.path.join(iconset_dir, f'icon_512x512@2x.png')
                if os.path.exists(src):
                    os.rename(src, dst)
            else:
                src = os.path.join(temp_dir, f'icon_{size}x{size}.png')
                src_2x = os.path.join(temp_dir, f'icon_{size}x{size}@2x.png')
                dst = os.path.join(iconset_dir, f'icon_{size}x{size}.png')
                dst_2x = os.path.join(iconset_dir, f'icon_{size}x{size}@2x.png')
                
                if os.path.exists(src):
                    os.rename(src, dst)
                if os.path.exists(src_2x):
                    os.rename(src_2x, dst_2x)
        
        # Convert iconset to icns using macOS iconutil
        os.system(f'iconutil -c icns -o "{icns_path}" "{iconset_dir}"')
        
    finally:
        # Clean up
        try:
            os.system(f'rm -rf "{temp_dir}"')
        except:
            pass

def main():
    if not os.path.exists('icon.svg'):
        print("Error: icon.svg not found")
        sys.exit(1)
    
    # Convert to both formats
    convert_svg_to_ico('icon.svg', 'icon.ico')
    print("Successfully converted icon.svg to icon.ico")
    
    if sys.platform == 'darwin':
        convert_svg_to_icns('icon.svg', 'icon.icns')
        print("Successfully converted icon.svg to icon.icns")
    else:
        print("Skipping .icns creation (requires macOS)")

if __name__ == '__main__':
    main() 