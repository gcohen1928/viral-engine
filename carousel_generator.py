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
        
        # TikTok examples for few-shot prompting
        self.good_examples = [
            # High performing TikTok examples (5k+ views)
            {"copy": "POV: you're trying to become that girl", "views": "11.8k"},
            {"copy": "This is the dumbest way to be a consistent runner but it worked", "views": "7.9k"},
            {"copy": "How to become a running girlie (step by step)", "views": "7.2k"},
            {"copy": "I never thought I'd be a runner. i hated cardio and thought it was dumb", "views": "5.2k"},
            {"copy": "I got into running for the dumbest reason", "views": "5.2k"},
            {"copy": "POV: you're trying to become that girl", "views": "3.3k"},
            {"copy": "POV: you gaslit yourself into running", "views": "1.8k"},
            {"copy": "i bought a matching set and brooks after my first run. i felt like being financially tied to the sport will motivate me to keep running", "views": "1.8k"},
        ]
        
        self.bad_examples = [
            # Low performing TikTok examples (<400 views)
            {"copy": "POV: you're becoming a running girlie", "views": "308"},
            {"copy": "Why is every run just me not trying to fall apart?? Anyone else??", "views": "350"},
            {"copy": "Here's how running saved our relationship (1/5)", "views": "276"},
        ]
        
        self.bad_examples = [
            # Add your 3 bad TikTok examples here (<400 views)
            {"copy": "BAD_EXAMPLE_1", "views": "<400"},
            {"copy": "BAD_EXAMPLE_2", "views": "<400"},
            {"copy": "BAD_EXAMPLE_3", "views": "<400"},
        ]
        
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
        
    def get_carousel_images(self, slide_count: int) -> List[Dict]:
        """Fetch images for carousel: selfie first, leo-screenshot last, random middle"""
        
        # Validate folder IDs
        missing_folders = [name for name, folder_id in self.folder_ids.items() if not folder_id]
        if missing_folders:
            raise ValueError(f"Missing folder IDs for: {', '.join(missing_folders)}")
        
        if slide_count < 2:
            raise ValueError("Need at least 2 slides (selfie + leo-screenshot)")
            
        images = []
        
        # Slide 1: Always selfie
        print(f"📁 Slide 1: Fetching from selfies...")
        selfie_image = self.get_random_image_from_folder(self.folder_ids['selfies'], 'selfies')
        images.append(selfie_image)
        print(f"✓ Selected: {selfie_image['name']}")
        
        # Middle slides: Random from legs, paths, friends
        middle_folders = ['legs', 'paths', 'friends']
        for i in range(2, slide_count):  # slides 2 to n-1
            folder_name = random.choice(middle_folders)
            folder_id = self.folder_ids[folder_name]
            
            print(f"📁 Slide {i}: Fetching from {folder_name}...")
            image = self.get_random_image_from_folder(folder_id, folder_name)
            images.append(image)
            print(f"✓ Selected: {image['name']}")
        
        # Last slide: Always leo-screenshot
        print(f"📁 Slide {slide_count}: Fetching from leo-screenshots...")
        leo_image = self.get_random_image_from_folder(self.folder_ids['leo_screenshots'], 'leo_screenshots')
        images.append(leo_image)
        print(f"✓ Selected: {leo_image['name']}")
                
        return images
    
    def build_few_shot_examples(self) -> str:
        """Build few-shot examples from TikTok data"""
        
        examples_text = "Here are examples of TikTok copy performance:\n\n"
        
        examples_text += "HIGH PERFORMING EXAMPLES (5k+ views):\n"
        for i, example in enumerate(self.good_examples[:4], 1):  # Show 4 good examples
            examples_text += f"{i}. \"{example['copy']}\" - {example['views']} views\n"
        
        examples_text += "\nLOW PERFORMING EXAMPLES (<400 views):\n"
        for i, example in enumerate(self.bad_examples, 1):  # Show all bad examples
            examples_text += f"{i}. \"{example['copy']}\" - {example['views']} views\n"
            
        examples_text += "\nBased on these patterns, create copy that follows the high-performing style.\n"
        
        return examples_text
        
    def generate_dynamic_prompt(self, slide_count: int, images: List[Dict]) -> str:
        """Generate dynamic prompt based on slide count and images"""
        
        # Build image context
        image_context = f"I'm providing you with {slide_count} images:\n"
        image_context += "Image 1: From 'selfies' folder (always first slide)\n"
        
        for i in range(2, slide_count):
            image_context += f"Image {i}: From '{images[i-1]['folder']}' folder\n"
            
        image_context += f"Image {slide_count}: From 'leo-screenshots' folder (always last slide)\n"
        
        # Build few-shot examples
        few_shot_examples = self.build_few_shot_examples()
        
        # Dynamic slide structure
        if slide_count == 3:
            structure = """
Create a 3-slide carousel:
- Slide 1: Strong hook/attention grabber
- Slide 2: Main value/insight 
- Slide 3: Call-to-action with leo screenshot
"""
        elif slide_count == 4:
            structure = """
Create a 4-slide carousel:
- Slide 1: Strong hook/attention grabber
- Slide 2: Problem/pain point
- Slide 3: Solution/insight
- Slide 4: Call-to-action with leo screenshot  
"""
        elif slide_count == 5:
            structure = """
Create a 5-slide carousel:
- Slide 1: Strong hook/attention grabber
- Slide 2: Problem/setup
- Slide 3: Insight/tip #1
- Slide 4: Insight/tip #2  
- Slide 5: Call-to-action with leo screenshot
"""
        else:
            structure = f"""
Create a {slide_count}-slide carousel:
- Slide 1: Strong hook/attention grabber
- Slides 2-{slide_count-1}: Value/insights/tips
- Slide {slide_count}: Call-to-action with leo screenshot
"""

        prompt = f"""
{image_context}

{few_shot_examples}

{structure}

Requirements:
- Use proven high-performing patterns from the examples above
- Keep each slide concise and punchy
- Use relevant emojis sparingly 
- Make slide 1 a strong hook that stops scrolling
- End with clear call-to-action on final slide
- Relate to image content when possible

Return ONLY the {slide_count} slide texts, one per line, numbered 1-{slide_count}.
"""
        
        return prompt
        
    def generate_carousel_copy(self, slide_count: int, images: List[Dict]) -> List[str]:
        """Generate carousel copy using OpenAI Vision API with dynamic prompting"""
        
        # Prepare images for OpenAI
        image_messages = []
        for i, img in enumerate(images):
            image_messages.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{img['base64']}"
                }
            })
        
        # Generate dynamic prompt
        prompt = self.generate_dynamic_prompt(slide_count, images)
        
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
            max_tokens=600
        )
        
        copy_text = response.choices[0].message.content
        slides = [line.strip() for line in copy_text.split('\n') if line.strip()]
        
        # Clean up numbering if present
        cleaned_slides = []
        for slide in slides:
            if slide.startswith(tuple(f'{i}.' for i in range(1, slide_count+1))):
                cleaned_slides.append(slide[2:].strip())
            elif slide.startswith(tuple(f'{i}:' for i in range(1, slide_count+1))):
                cleaned_slides.append(slide[2:].strip())
            else:
                cleaned_slides.append(slide)
                
        return cleaned_slides[:slide_count]  # Ensure correct number of slides
        
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
            
            print(f"Creating slide {i+1}/{len(copy_texts)} with {image['folder']} image...")
            
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
        
    def download_and_save_images(self, image_urls: List[str], slide_count: int, output_dir: str = "generated_carousel") -> List[str]:
        """Download generated images and save locally"""
        
        os.makedirs(output_dir, exist_ok=True)
        saved_paths = []
        
        # Create subfolder with timestamp and slide count
        timestamp = int(time.time())
        carousel_dir = os.path.join(output_dir, f"{slide_count}_slides_{timestamp}")
        os.makedirs(carousel_dir, exist_ok=True)
        
        for i, url in enumerate(image_urls):
            if url:
                response = requests.get(url)
                if response.status_code == 200:
                    filename = f"slide_{i+1}.png"
                    filepath = os.path.join(carousel_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                        
                    saved_paths.append(filepath)
                    print(f"✓ Downloaded: {filepath}")
                    
        return saved_paths
        
    def generate_carousel(self, slide_count: int = 5) -> List[str]:
        """Main function to generate complete carousel"""
        
        print(f"🎯 Starting {slide_count}-slide carousel generation...")
        
        # Step 1: Get specific images based on slide count
        print(f"📁 Fetching images for {slide_count} slides...")
        images = self.get_carousel_images(slide_count)
        print(f"✓ Retrieved {len(images)} images")
        
        # Step 2: Generate copy with OpenAI
        print("🤖 Generating carousel copy with OpenAI...")
        copy_texts = self.generate_carousel_copy(slide_count, images)
        print(f"✓ Generated copy for {slide_count} slides")
        for i, text in enumerate(copy_texts, 1):
            print(f"   Slide {i}: {text[:50]}...")
            
        # Step 3: Create images with BannerBear
        print("🎨 Creating carousel images with BannerBear...")
        image_urls = self.create_bannerbear_images(copy_texts, images)
        
        # Step 4: Download and save final images
        print("💾 Downloading final images...")
        saved_paths = self.download_and_save_images(image_urls, slide_count)
        
        print(f"🎉 {slide_count}-slide carousel generation complete!")
        print(f"📂 Images saved in: {saved_paths[0].split('/')[0]}/")
        
        return saved_paths

def main():
    """Main function with configurable slide count"""
    
    # Get slide count from user
    try:
        slide_count = input("How many slides do you want? (2-10, default 5): ")
        slide_count = int(slide_count) if slide_count.strip() else 5
        
        if slide_count < 2 or slide_count > 10:
            print("⚠️  Using default of 5 slides (must be 2-10)")
            slide_count = 5
            
    except ValueError:
        print("⚠️  Invalid input, using default of 5 slides")
        slide_count = 5
    
    generator = CarouselGenerator()
    try:
        carousel_paths = generator.generate_carousel(slide_count)
        print(f"\n🚀 Ready to post! Your {slide_count}-slide carousel is ready.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()