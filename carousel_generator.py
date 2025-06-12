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
        self.drive_folder_id = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
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
        
    def get_random_images(self, count: int = 3) -> List[Dict]:
        """Fetch random images from Google Drive folder"""
        if not self.drive_service:
            self.authenticate_google_drive()
            
        query = f"'{self.drive_folder_id}' in parents and mimeType contains 'image/'"
        results = self.drive_service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        if len(files) < count:
            raise ValueError(f"Not enough images in folder. Found {len(files)}, need {count}")
            
        selected_files = random.sample(files, count)
        
        images = []
        for file in selected_files:
            file_content = self.drive_service.files().get_media(fileId=file['id']).execute()
            images.append({
                'id': file['id'],
                'name': file['name'],
                'content': file_content,
                'base64': base64.b64encode(file_content).decode('utf-8')
            })
            
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
        
        prompt = """
        I need you to generate copy for a 5-slide carousel post. I'm providing you with some images as inspiration.
        
        Here are some examples of good carousel copy:
        
        Slide 1: "5 Marketing Mistakes That Are Killing Your Growth 🚫"
        Slide 2: "Mistake #1: Ignoring Your Analytics Data 📊"
        Slide 3: "Mistake #2: Posting Without a Strategy 📝"
        Slide 4: "Mistake #3: Not Engaging With Your Audience 💬"
        Slide 5: "Ready to Fix These? Comment 'GROWTH' below! 🚀"
        
        Based on the images provided, create engaging carousel copy that:
        - Has a strong hook on slide 1
        - Provides value in slides 2-4
        - Ends with a clear call-to-action on slide 5
        - Uses relevant emojis
        - Is concise and engaging
        
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
        """Create carousel images using BannerBear API"""
        
        generated_images = []
        
        for i, text in enumerate(copy_texts):
            # Use the first image for all slides, or cycle through images
            image_to_use = images[i % len(images)]
            
            payload = {
                "template": self.bannerbear_template_id,
                "modifications": [
                    {
                        "name": "text_layer",  # Adjust to your template's text layer name
                        "text": text
                    },
                    {
                        "name": "image_layer",  # Adjust to your template's image layer name  
                        "image_url": f"data:image/jpeg;base64,{image_to_use['base64']}"
                    }
                ]
            }
            
            headers = {
                "Authorization": f"Bearer {self.bannerbear_api_key}",
                "Content-Type": "application/json"
            }
            
            print(f"Creating slide {i+1}/5...")
            
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
        
        # Step 1: Get random images from Google Drive
        print("📁 Fetching random images from Google Drive...")
        images = self.get_random_images(count=3)
        print(f"✓ Retrieved {len(images)} images")
        
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