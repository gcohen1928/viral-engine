#!/usr/bin/env python3
import os
import sys
from carousel_generator import CarouselGenerator

def test_google_drive():
    """Test Google Drive connection"""
    print("🧪 Testing Google Drive connection...")
    
    try:
        generator = CarouselGenerator()
        generator.authenticate_google_drive()
        
        folder_names = ['selfies', 'legs', 'paths', 'friends', 'leo_screenshots']
        
        for folder_name in folder_names:
            folder_id = generator.folder_ids[folder_name]
            if not folder_id:
                print(f"❌ Missing folder ID for {folder_name}")
                return False
                
            # Try to list files in each folder
            query = f"'{folder_id}' in parents and mimeType contains 'image/'"
            results = generator.drive_service.files().list(
                q=query,
                fields="files(id, name, mimeType)"
            ).execute()
            
            files = results.get('files', [])
            print(f"✓ {folder_name}: {len(files)} images")
            
            if len(files) == 0:
                print(f"⚠️  Warning: No images in {folder_name} folder")
            else:
                # Show first image as example
                print(f"   Example: {files[0]['name']}")
        
        print(f"✓ Google Drive connected successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Google Drive test failed: {e}")
        return False

def test_openai():
    """Test OpenAI connection"""
    print("\n🧪 Testing OpenAI connection...")
    
    try:
        generator = CarouselGenerator()
        
        # Simple text completion test
        response = generator.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'API test successful'"}],
            max_tokens=10
        )
        
        result = response.choices[0].message.content
        print(f"✓ OpenAI connected successfully!")
        print(f"✓ Response: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenAI test failed: {e}")
        return False

def test_bannerbear():
    """Test BannerBear connection"""
    print("\n🧪 Testing BannerBear connection...")
    
    try:
        import requests
        generator = CarouselGenerator()
        
        headers = {
            "Authorization": f"Bearer {generator.bannerbear_api_key}",
        }
        
        # Test API connection by getting account info
        response = requests.get(
            "https://api.bannerbear.com/v2/account",
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✓ BannerBear connected successfully!")
            account_info = response.json()
            print(f"✓ Account: {account_info.get('name', 'Unknown')}")
            
            # Test template exists
            template_response = requests.get(
                f"https://api.bannerbear.com/v2/templates/{generator.bannerbear_template_id}",
                headers=headers
            )
            
            if template_response.status_code == 200:
                template_info = template_response.json()
                print(f"✓ Template found: {template_info.get('name', 'Unknown')}")
                return True
            else:
                print(f"❌ Template not found: {template_response.status_code}")
                return False
                
        else:
            print(f"❌ BannerBear connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ BannerBear test failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("🧪 Testing environment setup...")
    
    required_vars = [
        'OPENAI_API_KEY',
        'BANNERBEAR_API_KEY', 
        'BANNERBEAR_TEMPLATE_ID',
        'SELFIES_FOLDER_ID',
        'LEGS_FOLDER_ID',
        'PATHS_FOLDER_ID',
        'FRIENDS_FOLDER_ID',
        'LEO_SCREENSHOTS_FOLDER_ID'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_vars.append(var)
        else:
            print(f"✓ {var}: {'*' * 8}...{value[-4:]}")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✓ All environment variables set")
        return True

def main():
    """Run all tests"""
    print("🚀 Running component tests...\n")
    
    results = []
    
    # Test environment first
    results.append(test_environment())
    
    if results[-1]:  # Only continue if env is good
        results.append(test_google_drive())
        results.append(test_openai())
        results.append(test_bannerbear())
    
    print(f"\n📊 Test Results:")
    print(f"Environment: {'✅' if results[0] else '❌'}")
    
    if len(results) > 1:
        print(f"Google Drive: {'✅' if results[1] else '❌'}")
        print(f"OpenAI: {'✅' if results[2] else '❌'}")
        print(f"BannerBear: {'✅' if results[3] else '❌'}")
        
        if all(results):
            print("\n🎉 All tests passed! Ready to generate carousels.")
        else:
            print("\n❌ Some tests failed. Fix the issues above before running the main script.")
    else:
        print("\n❌ Environment setup incomplete. Please configure your .env file.")

if __name__ == "__main__":
    main()