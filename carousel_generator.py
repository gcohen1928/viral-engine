#!/usr/bin/env python3
import os
import random
import base64
import json
import time
from io import BytesIO
from typing import List, Dict, Any

import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

class CarouselGenerator:
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.bannerbear_api_key = os.getenv('BANNERBEAR_API_KEY')
        self.bannerbear_template_id = os.getenv('BANNERBEAR_TEMPLATE_ID')
        
        # Load all 5 folder IDs
        self.folder_ids = {
            'selfies': os.getenv('SELFIES_FOLDER_ID'),
            'legs': os.getenv('LEGS_FOLDER_ID'), 
            'paths': os.getenv('PATHS_FOLDER_ID'),
            'friends': os.getenv('FRIENDS_FOLDER_ID'),
            'leo_screenshots': os.getenv('LEO_SCREENSHOTS_FOLDER_ID')
        }
        
        self.drive_service = None
        
    def authenticate_google_drive(self):
        """Authenticate with Google Drive API"""
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        self.drive_service = build('drive', 'v3', credentials=creds)
        
    def get_random_image_from_folder(self, folder_id: str, folder_name: str) -> Dict:
        """Fetch one random image from specific folder"""
        if not self.drive_service:
            self.authenticate_google_drive()
            
        query = f"'{folder_id}' in parents and mimeType contains 'image/'"
        results = self.drive_service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        if not files:
            raise ValueError(f"No images found in {folder_name} folder (ID: {folder_id})")
            
        # Pick random image
        selected_file = random.choice(files)
        
        # Download image content
        file_content = self.drive_service.files().get_media(fileId=selected_file['id']).execute()
        
        return {
            'id': selected_file['id'],
            'name': selected_file['name'],
            'folder': folder_name,
            'content': file_content,
            'base64': base64.b64encode(file_content).decode('utf-8')
        }
        
    def get_carousel_images(self) -> List[Dict]:
        """Fetch one random image from each of the 5 folders"""
        
        # Validate folder IDs
        missing_folders = [name for name, folder_id in self.folder_ids.items() if not folder_id]
        if missing_folders:
            raise ValueError(f"Missing folder IDs for: {', '.join(missing_folders)}")
        
        images = []
        folder_order = ['selfies', 'legs', 'paths', 'friends', 'leo_screenshots']
        
        for folder_name in folder_order:
            folder_id = self.folder_ids[folder_name]
            print(f"📁 Fetching random image from {folder_name}...")
            
            try:
                image = self.get_random_image_from_folder(folder_id, folder_name)
                images.append(image)
                print(f"✓ Selected: {image['name']}")
            except Exception as e:
                print(f"❌ Error with {folder_name} folder: {e}")
                raise
                
        return images
        
    def generate_carousel_copy(self, images: List[Dict]) -> List[str]:
        """Generate carousel copy using OpenAI Vision API"""
        
        # Prepare images for OpenAI
        image_messages = []
        for i, img in enumerate(images):
            image_messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img['base64']}"
                }
            })
        
        # Enhanced prompt with folder context
        prompt = f"""
        I need you to generate copy for a 5-slide carousel post. I'm providing you with 5 images:
        
        Image 1: From "selfies" folder
        Image 2: From "legs" folder  
        Image 3: From "paths" folder
        Image 4: From "friends" folder
        Image 5: From "leo-screenshots" folder
        
        Here are some examples of good carousel copy:
        
        Slide 1: "5 Marketing Mistakes That Are Killing Your Growth 🚫"
        Slide 2: "Mistake #1: Ignoring Your Analytics Data 📊"
        Slide 3: "Mistake #2: Posting Without a Strategy 📝"
        Slide 4: "Mistake #3: Not Engaging With Your Audience 💬"
        Slide 5: "Ready to Fix These? Comment 'GROWTH' below! 🚀"
        
        Based on the images provided and their context, create engaging carousel copy that:
        - Has a strong hook on slide 1 
        - Provides value in slides 2-4
        - Ends with a clear call-to-action on slide 5
        - Uses relevant emojis
        - Is concise and engaging
        - Relates to the image content when possible
        
        Return ONLY the 5 slide texts, one per line, numbered 1-5.
        """
        
        messages = [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": prompt},
                    *image_messages
                ]
            }
        ]
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=messages,
            max_tokens=500
        )
        
        copy_text = response.choices[0].message.content
        slides = [line.strip() for line in copy_text.split('\n') if line.strip()]
        
        # Clean up numbering if present
        cleaned_slides = []
        for slide in slides:
            if slide.startswith(('1.', '2.', '3.', '4.', '5.')):
                cleaned_slides.append(slide[2:].strip())
            elif slide.startswith(('1:', '2:', '3:', '4:', '5:')):
                cleaned_slides.append(slide[2:].strip())
            else:
                cleaned_slides.append(slide)
                
        return cleaned_slides[:5]  # Ensure only 5 slides
        
    def create_bannerbear_images(self, copy_texts: List[str], images: List[Dict]) -> List[str]:
        """Create carousel images using BannerBear API with specific image for each slide"""
        
        generated_images = []
        
        for i, (text, image) in enumerate(zip(copy_texts, images)):
            
            payload = {
                "template": self.bannerbear_template_id,
                "modifications": [
                    {
                        "name": "text_layer",  # Adjust to your template's text layer name
                        "text": text
                    },
                    {
                        "name": "image_layer",  # Adjust to your template's image layer name  
                        "image_url": f"data:image/jpeg;base64,{image['base64']}"
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.bannerbear_api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"Creating slide {i+1}/5 with {image['folder']} image...")
            
            response = requests.post(
                "https://api.bannerbear.com/v2/images",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                result = response.json()
                image_url = result.get('image_url')
                generated_images.append(image_url)
                print(f"✓ Slide {i+1} created: {image_url}")
            else:
                print(f"✗ Error creating slide {i+1}: {response.status_code} - {response.text}")
                
            # Rate limiting
            time.sleep(2)
            
        return generated_images
        
    def download_and_save_images(self, image_urls: List[str], output_dir: str = "generated_carousel") -> List[str]:
        """Download generated images and save locally"""
        
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        
        for i, url in enumerate(image_urls):
            if url:
                response = requests.get(url)
                if response.status_code == 200:
                    filename = f"slide_{i+1}.png"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                        
                    saved_paths.append(filepath)
                    print(f"✓ Downloaded: {filepath}")
                    
        return saved_paths
        
    def generate_carousel(self) -> List[str]:
        """Main function to generate complete carousel"""
        
        print("🎯 Starting carousel generation...")
        
        # Step 1: Get specific images from each folder
        print("📁 Fetching images from 5 specific folders...")
        images = self.get_carousel_images()
        print(f"✓ Retrieved images from all 5 folders")
        
        # Step 2: Generate copy with OpenAI
        print("🤖 Generating carousel copy with OpenAI...")
        copy_texts = self.generate_carousel_copy(images)
        print("✓ Generated copy for 5 slides")
        for i, text in enumerate(copy_texts, 1):
            print(f"   Slide {i}: {text[:50]}...")
            
        # Step 3: Create images with BannerBear
        print("🎨 Creating carousel images with BannerBear...")
        image_urls = self.create_bannerbear_images(copy_texts, images)
        
        # Step 4: Download and save final images
        print("💾 Downloading final images...")
        saved_paths = self.download_and_save_images(image_urls)
        
        print(f"🎉 Carousel generation complete! Generated {len(saved_paths)} images")
        print(f"📂 Images saved in: generated_carousel/")
        
        return saved_paths

if __name__ == "__main__":
    generator = CarouselGenerator()
    try:
        carousel_paths = generator.generate_carousel()
        print("\n🚀 Ready to post! Your carousel images are ready.")
    except Exception as e:
        print(f"❌ Error: {e}")