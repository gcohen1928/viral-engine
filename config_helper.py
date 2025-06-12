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
        "image_url": f"data:image/jpeg;base64,{{image['base64']}}"
    }}
]""")
                
        else:
            print(f"❌ Failed to fetch template: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error inspecting template: {e}")

def list_google_drive_images():
    """List images in each of the 5 Google Drive folders"""
    
    try:
        from carousel_generator import CarouselGenerator
        
        generator = CarouselGenerator()
        generator.authenticate_google_drive()
        
        folder_info = {
            'selfies': 'SELFIES_FOLDER_ID',
            'legs': 'LEGS_FOLDER_ID', 
            'paths': 'PATHS_FOLDER_ID',
            'friends': 'FRIENDS_FOLDER_ID',
            'leo_screenshots': 'LEO_SCREENSHOTS_FOLDER_ID'
        }
        
        total_images = 0
        
        for folder_name, env_var in folder_info.items():
            folder_id = generator.folder_ids[folder_name]
            
            if not folder_id:
                print(f"❌ {folder_name}: Missing folder ID ({env_var})")
                continue
                
            query = f"'{folder_id}' in parents and mimeType contains 'image/'"
            results = generator.drive_service.files().list(
                q=query,
                fields="files(id, name, mimeType, size)",
                pageSize=50
            ).execute()
            
            files = results.get('files', [])
            total_images += len(files)
            
            print(f"📁 {folder_name.upper()}: {len(files)} images")
            
            if len(files) == 0:
                print(f"   ⚠️  No images found - check folder ID")
            elif len(files) <= 5:
                for i, file in enumerate(files, 1):
                    size_mb = int(file.get('size', 0)) / (1024 * 1024) if file.get('size') else 0
                    print(f"   {i}. {file['name']} ({size_mb:.1f}MB)")
            else:
                # Show first 3 images
                for i, file in enumerate(files[:3], 1):
                    size_mb = int(file.get('size', 0)) / (1024 * 1024) if file.get('size') else 0
                    print(f"   {i}. {file['name']} ({size_mb:.1f}MB)")
                print(f"   ... and {len(files) - 3} more")
            
            print()  # Empty line for readability
            
        print(f"📊 Total: {total_images} images across all folders")
        
        # Check for potential issues
        missing_folders = [name for name, folder_id in generator.folder_ids.items() if not folder_id]
        if missing_folders:
            print(f"\n⚠️  Missing folder IDs: {', '.join(missing_folders)}")
            
    except Exception as e:
        print(f"❌ Error listing Google Drive images: {e}")

def test_carousel_generation():
    """Test one complete carousel generation"""
    
    print("🧪 Testing complete carousel generation...")
    
    try:
        from carousel_generator import CarouselGenerator
        
        generator = CarouselGenerator()
        
        # Just test getting one image from each folder
        print("Testing image retrieval from each folder...")
        
        folder_names = ['selfies', 'legs', 'paths', 'friends', 'leo_screenshots']
        for folder_name in folder_names:
            folder_id = generator.folder_ids[folder_name]
            if folder_id:
                try:
                    image = generator.get_random_image_from_folder(folder_id, folder_name)
                    print(f"✓ {folder_name}: {image['name']}")
                except Exception as e:
                    print(f"❌ {folder_name}: {e}")
                    return False
            else:
                print(f"❌ {folder_name}: Missing folder ID")
                return False
        
        print("✅ All folders accessible! Ready for carousel generation.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    """Main configuration helper"""
    
    print("⚙️  Carousel Generator Configuration Helper\n")
    
    print("1️⃣  Inspecting BannerBear Template...")
    inspect_bannerbear_template()
    
    print("\n" + "="*60)
    
    print("\n2️⃣  Checking Google Drive Folders...")
    list_google_drive_images()
    
    print("\n" + "="*60)
    
    print("\n3️⃣  Testing Image Retrieval...")
    test_carousel_generation()

if __name__ == "__main__":
    main()