#!/usr/bin/env python3
"""
Automated Carousel Generator
- Fetches random images from Google Drive
- Generates copy using OpenAI
- Creates carousel slides using BannerBear
"""

import os
import random
import json
import requests
import base64
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class CarouselGenerator:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.bannerbear_api_key = os.getenv('BANNERBEAR_API_KEY')
        self.bannerbear_template_id = os.getenv('BANNERBEAR_TEMPLATE_ID')
        self.google_drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
        
        self.output_dir = Path('generated_carousels')
        self.output_dir.mkdir(exist_ok=True)
        
        self.temp_dir = Path('temp_images')
        self.temp_dir.mkdir(exist_ok=True)
        
        self.openai_client = OpenAI(api_key=self.openai_api_key)
        
    def authenticate_google_drive(self):
        """Authenticate and return Google Drive service"""
        SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        return build('drive', 'v3', credentials=creds)
    
    def get_random_images(self, count: int = 5) -> List[Dict[str, str]]:
        """Fetch random images from Google Drive"""
        service = self.authenticate_google_drive()
        
        query = f"'{self.google_drive_folder_id}' in parents and mimeType contains 'image/'"
        results = service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            raise Exception("No images found in the specified Google Drive folder")
        
        selected_files = random.sample(files, min(count, len(files)))
        downloaded_files = []
        
        for file in selected_files:
            file_path = self.temp_dir / file['name']
            request = service.files().get_media(fileId=file['id'])
            
            with open(file_path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            downloaded_files.append({
                'path': str(file_path),
                'name': file['name'],
                'id': file['id']
            })
        
        return downloaded_files
    
    def generate_carousel_copy(self, image_context: str = "") -> List[str]:
        """Generate carousel copy using OpenAI"""
        prompt = f"""Generate engaging copy for a 5-slide Instagram carousel. 
        
        Context: {image_context if image_context else "General lifestyle/business content"}
        
        Examples of good carousel copy:
        
        Slide 1: "5 Morning Habits That Changed My Life (swipe to see all →)"
        Slide 2: "1. Wake up at 5 AM - Your competition is still sleeping"
        Slide 3: "2. Cold shower - Mental toughness starts here"
        Slide 4: "3. No phone for first hour - Own your morning, own your day"
        Slide 5: "4. Exercise - Energy creates energy | 5. Plan your top 3 - Focus beats busy"
        
        Another example:
        
        Slide 1: "How I 10x'd My Productivity (steal this system)"
        Slide 2: "The Problem: Too many tasks, not enough time"
        Slide 3: "The Solution: Time-blocking + Energy management"
        Slide 4: "Morning: Deep work | Afternoon: Meetings | Evening: Admin"
        Slide 5: "Result: 3 hours of focused work > 8 hours of busy work"
        
        Generate copy for 5 slides with this style:
        - Slide 1: Hook with promise/curiosity
        - Slides 2-4: Value/tips/insights
        - Slide 5: Summary/CTA
        
        Keep each slide concise (under 30 words). Return ONLY the 5 slide texts, one per line."""
        
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a social media copywriting expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8
        )
        
        carousel_copy = response.choices[0].message.content.strip().split('\n')
        carousel_copy = [text.strip() for text in carousel_copy if text.strip()][:5]
        
        return carousel_copy
    
    def create_bannerbear_images(self, images: List[Dict[str, str]], texts: List[str]) -> List[str]:
        """Create carousel images using BannerBear API"""
        generated_urls = []
        
        headers = {
            'Authorization': f'Bearer {self.bannerbear_api_key}',
            'Content-Type': 'application/json'
        }
        
        for i, (image, text) in enumerate(zip(images, texts)):
            # Create the carousel slide with local image
            # BannerBear expects image URLs, so we'll need to provide a public URL
            # For now, let's modify to use the template's modifications properly
            
            with open(image['path'], 'rb') as f:
                image_data = f.read()
                
            # Convert to base64 for inline image
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            payload = {
                'template': self.bannerbear_template_id,
                'modifications': [
                    {
                        'name': 'image',  # This should match your template layer name
                        'image_url': f'data:image/jpeg;base64,{image_base64}'
                    },
                    {
                        'name': 'text',  # This should match your template text layer name
                        'text': text
                    },
                    {
                        'name': 'slide_number',  # Optional - if your template has this
                        'text': f"{i+1}/5"
                    }
                ],
                'webhook_url': None,
                'metadata': None
            }
            
            response = requests.post(
                'https://api.bannerbear.com/v2/images',
                headers=headers,
                json=payload
            )
            
            if response.status_code == 202:
                result = response.json()
                generated_urls.append(result['uid'])
            else:
                print(f"Failed to create slide {i+1}: {response.text}")
        
        # Wait for images to be generated and download them
        final_images = []
        for uid in generated_urls:
            final_url = self.wait_for_bannerbear_image(uid)
            if final_url:
                final_images.append(final_url)
        
        return final_images
    
    def wait_for_bannerbear_image(self, uid: str, max_attempts: int = 30) -> str:
        """Poll BannerBear API until image is ready"""
        headers = {'Authorization': f'Bearer {self.bannerbear_api_key}'}
        
        for _ in range(max_attempts):
            response = requests.get(
                f'https://api.bannerbear.com/v2/images/{uid}',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == 'completed':
                    return data['image_url_png']
            
            time.sleep(2)
        
        return None
    
    def download_final_images(self, image_urls: List[str]) -> List[str]:
        """Download generated images to output directory"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        carousel_dir = self.output_dir / f'carousel_{timestamp}'
        carousel_dir.mkdir(exist_ok=True)
        
        local_paths = []
        for i, url in enumerate(image_urls):
            response = requests.get(url)
            if response.status_code == 200:
                file_path = carousel_dir / f'slide_{i+1}.png'
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                local_paths.append(str(file_path))
        
        return local_paths
    
    def generate_carousel(self):
        """Main method to generate complete carousel"""
        print("🎨 Starting carousel generation...")
        
        try:
            print("📸 Fetching random images from Google Drive...")
            images = self.get_random_images(5)
            print(f"✅ Downloaded {len(images)} images")
            
            print("✍️  Generating carousel copy with OpenAI...")
            carousel_texts = self.generate_carousel_copy()
            print("✅ Generated carousel copy")
            
            for i, text in enumerate(carousel_texts):
                print(f"Slide {i+1}: {text}")
            
            print("🖼️  Creating carousel images with BannerBear...")
            image_urls = self.create_bannerbear_images(images, carousel_texts)
            print(f"✅ Created {len(image_urls)} carousel slides")
            
            print("💾 Downloading final images...")
            local_paths = self.download_final_images(image_urls)
            print(f"✅ Saved carousel to: {local_paths[0].rsplit('/', 1)[0]}")
            
            # Cleanup temp files
            for image in images:
                os.remove(image['path'])
            
            return local_paths
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise

if __name__ == "__main__":
    generator = CarouselGenerator()
    carousel_paths = generator.generate_carousel()
    print("\n🎉 Carousel generation complete!")
    print("📁 Images saved at:")
    for path in carousel_paths:
        print(f"   - {path}")