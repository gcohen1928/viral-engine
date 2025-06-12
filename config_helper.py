#!/usr/bin/env python3
import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def inspect_bannerbear_template():
    """Inspect BannerBear template to find layer names"""
    
    api_key = os.getenv('BANNERBEAR_API_KEY')
    template_id = os.getenv('BANNERBEAR_TEMPLATE_ID')
    
    if not api_key or not template_id:
        print("❌ Please set BANNERBEAR_API_KEY and BANNERBEAR_TEMPLATE_ID in .env first")
        return
    
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    try:
        response = requests.get(
            f"https://api.bannerbear.com/v2/templates/{template_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            template = response.json()
            
            print(f"📋 Template: {template.get('name', 'Unknown')}")
            print(f"🆔 ID: {template_id}")
            print("\n🎨 Available Layers:")
            
            layers = template.get('available_modifications', [])
            text_layers = []
            image_layers = []
            
            for layer in layers:
                layer_type = layer.get('type', 'unknown')
                layer_name = layer.get('name', 'unnamed')
                
                if layer_type == 'text':
                    text_layers.append(layer_name)
                    print(f"   📝 Text: {layer_name}")
                elif layer_type == 'image':
                    image_layers.append(layer_name)
                    print(f"   🖼️  Image: {layer_name}")
                else:
                    print(f"   ❓ Other: {layer_name} ({layer_type})")
            
            print("\n💡 Suggested layer names for your script:")
            if text_layers:
                print(f"   Text layer: '{text_layers[0]}'")
            if image_layers:
                print(f"   Image layer: '{image_layers[0]}'")
                
            # Generate updated code snippet
            if text_layers and image_layers:
                print(f"\n📋 Update this in carousel_generator.py:")
                print(f"""
"modifications": [
    {{
        "name": "{text_layers[0]}",  # Text layer
        "text": text
    }},
    {{
        "name": "{image_layers[0]}",  # Image layer
        "image_url": f"data:image/jpeg;base64,{{image_to_use['base64']}}"
    }}
]""")
                
        else:
            print(f"❌ Failed to fetch template: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error inspecting template: {e}")

def list_google_drive_images():
    """List images in Google Drive folder to verify setup"""
    
    try:
        from carousel_generator import CarouselGenerator
        
        generator = CarouselGenerator()
        generator.authenticate_google_drive()
        
        query = f"'{generator.drive_folder_id}' in parents and mimeType contains 'image/'"
        results = generator.drive_service.files().list(
            q=query,
            fields="files(id, name, mimeType, size)",
            pageSize=20
        ).execute()
        
        files = results.get('files', [])
        
        print(f"📁 Found {len(files)} images in Google Drive folder:")
        
        for i, file in enumerate(files, 1):
            size_mb = int(file.get('size', 0)) / (1024 * 1024) if file.get('size') else 0
            print(f"   {i:2d}. {file['name']} ({size_mb:.1f}MB)")
            
        if len(files) < 3:
            print(f"\n⚠️  Warning: Only {len(files)} images found. Need at least 3 for carousel generation.")
            
    except Exception as e:
        print(f"❌ Error listing Google Drive images: {e}")

def main():
    """Main configuration helper"""
    
    print("⚙️  Carousel Generator Configuration Helper\n")
    
    print("1️⃣  Inspecting BannerBear Template...")
    inspect_bannerbear_template()
    
    print("\n" + "="*50)
    
    print("\n2️⃣  Checking Google Drive Images...")
    list_google_drive_images()

if __name__ == "__main__":
    main()