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

def test_configurable_generation():
    """Test configurable slide generation with different counts"""
    
    print("🧪 Testing configurable carousel generation...")
    
    try:
        from carousel_generator import CarouselGenerator
        
        generator = CarouselGenerator()
        
        # Test different slide counts
        test_counts = [3, 4, 5, 6]
        
        for slide_count in test_counts:
            print(f"\n📋 Testing {slide_count}-slide carousel:")
            
            try:
                # Test image selection
                images = generator.get_carousel_images(slide_count)
                
                print(f"   Images: selfie → ", end="")
                for i in range(1, slide_count - 1):
                    print(f"{images[i]['folder']} → ", end="")
                print("leo-screenshot")
                
                # Test prompt generation  
                prompt = generator.generate_dynamic_prompt(slide_count, images)
                
                if f"{slide_count} images" in prompt:
                    print(f"   ✓ Prompt correctly references {slide_count} slides")
                else:
                    print(f"   ❌ Prompt doesn't reference {slide_count} slides")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                
        print("\n✅ Configurable generation test complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

def check_tiktok_examples():
    """Check TikTok examples status"""
    
    print("📱 Checking TikTok examples...")
    
    try:
        from carousel_generator import CarouselGenerator
        
        generator = CarouselGenerator()
        
        print(f"✓ Good examples: {len(generator.good_examples)}")
        print(f"✓ Bad examples: {len(generator.bad_examples)}")
        
        # Check for placeholders
        placeholders = 0
        for example in generator.good_examples + generator.bad_examples:
            if "EXAMPLE" in example['copy']:
                placeholders += 1
        
        if placeholders > 0:
            print(f"\n⚠️  Found {placeholders} placeholder examples")
            print("💡 Run: python3 add_tiktok_examples.py to add real data")
        else:
            print("\n✅ Real TikTok examples loaded!")
            
            # Show first few examples
            print("\nSample good examples:")
            for i, example in enumerate(generator.good_examples[:3], 1):
                preview = example['copy'][:50] + "..." if len(example['copy']) > 50 else example['copy']
                print(f"   {i}. \"{preview}\" - {example['views']} views")
                
    except Exception as e:
        print(f"❌ Error checking TikTok examples: {e}")

def test_carousel_generation():
    """Test one complete carousel generation"""
    
    print("🧪 Testing complete carousel generation...")
    
    try:
        from carousel_generator import CarouselGenerator
        
        generator = CarouselGenerator()
        
        # Just test getting one image from each folder for 5 slides
        print("Testing image retrieval for 5 slides...")
        
        slide_count = 5
        images = generator.get_carousel_images(slide_count)
        
        if len(images) == slide_count:
            print(f"✓ Retrieved {len(images)} images correctly")
            
            # Show the structure
            structure = []
            for i, img in enumerate(images, 1):
                structure.append(f"Slide {i}: {img['folder']}")
                
            print("   " + " → ".join([img['folder'] for img in images]))
            
        else:
            print(f"❌ Expected {slide_count} images, got {len(images)}")
            return False
        
        print("✅ Image retrieval test passed!")
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
    
    print("\n3️⃣  Testing Configurable Generation...")
    test_configurable_generation()
    
    print("\n" + "="*60)
    
    print("\n4️⃣  Checking TikTok Examples...")
    check_tiktok_examples()
    
    print("\n" + "="*60)
    
    print("\n5️⃣  Testing Image Retrieval...")
    test_carousel_generation()

if __name__ == "__main__":
    main()