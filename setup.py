#!/usr/bin/env python3
"""
Setup script for Carousel Generator
Helps with Google Drive OAuth setup
"""

import os
import json
from pathlib import Path

def setup_google_oauth():
    print("🔧 Setting up Google Drive OAuth...")
    print("\nTo use this script, you need to:")
    print("1. Go to https://console.cloud.google.com/")
    print("2. Create a new project or select existing")
    print("3. Enable Google Drive API")
    print("4. Create OAuth 2.0 credentials (Desktop application)")
    print("5. Download the credentials JSON file")
    
    creds_path = input("\nEnter path to your downloaded credentials JSON file: ").strip()
    
    if os.path.exists(creds_path):
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        with open('credentials.json', 'w') as f:
            json.dump(creds_data, f, indent=2)
        
        print("✅ Credentials saved to credentials.json")
        print("\nThe first time you run the carousel generator, it will:")
        print("1. Open a browser window for authentication")
        print("2. Ask you to authorize access to your Google Drive")
        print("3. Save the auth token for future use")
    else:
        print("❌ File not found. Please check the path and try again.")

def create_env_file():
    print("\n📝 Creating .env file...")
    
    if os.path.exists('.env'):
        overwrite = input(".env file already exists. Overwrite? (y/N): ").lower()
        if overwrite != 'y':
            return
    
    env_content = []
    
    openai_key = input("Enter your OpenAI API key: ").strip()
    env_content.append(f"OPENAI_API_KEY={openai_key}")
    
    bannerbear_key = input("Enter your BannerBear API key: ").strip()
    env_content.append(f"BANNERBEAR_API_KEY={bannerbear_key}")
    
    template_id = input("Enter your BannerBear template ID: ").strip()
    env_content.append(f"BANNERBEAR_TEMPLATE_ID={template_id}")
    
    print("\nTo get your Google Drive folder ID:")
    print("1. Navigate to the folder in Google Drive")
    print("2. The URL will look like: https://drive.google.com/drive/folders/FOLDER_ID")
    print("3. Copy the FOLDER_ID part")
    
    folder_id = input("\nEnter your Google Drive folder ID: ").strip()
    env_content.append(f"GOOGLE_DRIVE_FOLDER_ID={folder_id}")
    
    env_content.append("\n# Optional settings")
    env_content.append("OPENAI_MODEL=gpt-4")
    env_content.append("CAROUSEL_SLIDES=5")
    
    with open('.env', 'w') as f:
        f.write('\n'.join(env_content))
    
    print("✅ .env file created successfully!")

def main():
    print("🎨 Carousel Generator Setup")
    print("=" * 40)
    
    # Create necessary directories
    Path('generated_carousels').mkdir(exist_ok=True)
    Path('temp_images').mkdir(exist_ok=True)
    
    # Setup Google OAuth
    setup_oauth = input("\nSet up Google Drive OAuth? (Y/n): ").lower()
    if setup_oauth != 'n':
        setup_google_oauth()
    
    # Create .env file
    create_env = input("\nCreate .env file? (Y/n): ").lower()
    if create_env != 'n':
        create_env_file()
    
    print("\n✨ Setup complete!")
    print("\nNext steps:")
    print("1. Run: pip install -r requirements.txt")
    print("2. Make sure your BannerBear template has layers named: 'image', 'text', 'slide_number'")
    print("3. Run: python carousel_generator.py")

if __name__ == "__main__":
    main()