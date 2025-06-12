#!/usr/bin/env python3
import os
import json
import sys

def setup_project():
    print("🚀 Setting up Carousel Generator...")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# API Keys
OPENAI_API_KEY=your_openai_api_key_here
BANNERBEAR_API_KEY=your_bannerbear_api_key_here
BANNERBEAR_TEMPLATE_ID=your_template_id_here

# Google Drive Folder IDs (get from folder URLs)
SELFIES_FOLDER_ID=your_selfies_folder_id_here
LEGS_FOLDER_ID=your_legs_folder_id_here
PATHS_FOLDER_ID=your_paths_folder_id_here
FRIENDS_FOLDER_ID=your_friends_folder_id_here
LEO_SCREENSHOTS_FOLDER_ID=your_leo_screenshots_folder_id_here
""")
        print("✓ Created .env file - PLEASE FILL IN YOUR API KEYS AND FOLDER IDs!")
    else:
        print("✓ .env file already exists")
    
    # Google Drive folder setup instructions
    print("\n📁 Google Drive Folder Setup:")
    print("Create these 5 folders in Google Drive:")
    print("1. selfies")
    print("2. legs") 
    print("3. paths")
    print("4. friends")
    print("5. leo-screenshots")
    print("\nAdd images to each folder, then get folder IDs from URLs")
    
    # Check for Google credentials
    if not os.path.exists('credentials.json'):
        print("\n🔑 Google Drive API Setup Required:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Drive API")
        print("4. Create credentials (OAuth 2.0 client ID)")
        print("5. Download the JSON file and save as 'credentials.json'")
        print("6. Make sure to add your email to test users if in testing mode")
    else:
        print("✓ credentials.json found")
    
    # Instructions for BannerBear
    print("\n🎨 BannerBear Setup Instructions:")
    print("1. Create template in BannerBear dashboard")
    print("2. Note the layer names (text_layer, image_layer)")
    print("3. Update layer names in carousel_generator.py if different")
    print("4. Get your template ID and API key")
    
    # Create directories
    os.makedirs('generated_carousel', exist_ok=True)
    print("\n📁 Created output directory: generated_carousel/")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Create 5 folders in Google Drive with images")
    print("2. Fill in your .env file with real API keys and folder IDs")
    print("3. Add credentials.json from Google Cloud Console")
    print("4. Test: python3 config_helper.py")
    print("5. Run: python3 carousel_generator.py")

if __name__ == "__main__":
    setup_project()