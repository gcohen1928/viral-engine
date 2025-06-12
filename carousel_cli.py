#!/usr/bin/env python3
"""
CLI for Carousel Generator with additional options
"""

import argparse
import sys
from carousel_generator import CarouselGenerator
import requests
import base64
from pathlib import Path

class ImgBBUploader:
    """Upload images to ImgBB for public URLs"""
    def __init__(self, api_key):
        self.api_key = api_key
        self.upload_url = "https://api.imgbb.com/1/upload"
    
    def upload_image(self, image_path):
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
        
        payload = {
            'key': self.api_key,
            'image': image_data
        }
        
        response = requests.post(self.upload_url, data=payload)
        if response.status_code == 200:
            return response.json()['data']['url']
        return None

class EnhancedCarouselGenerator(CarouselGenerator):
    def __init__(self, use_imgbb=False, imgbb_key=None):
        super().__init__()
        self.use_imgbb = use_imgbb
        self.imgbb_uploader = ImgBBUploader(imgbb_key) if imgbb_key else None
    
    def create_bannerbear_images(self, images, texts):
        """Override to support image hosting"""
        if self.use_imgbb and self.imgbb_uploader:
            return self._create_with_hosted_images(images, texts)
        return super().create_bannerbear_images(images, texts)
    
    def _create_with_hosted_images(self, images, texts):
        """Create carousel using hosted image URLs"""
        generated_urls = []
        
        headers = {
            'Authorization': f'Bearer {self.bannerbear_api_key}',
            'Content-Type': 'application/json'
        }
        
        for i, (image, text) in enumerate(zip(images, texts)):
            print(f"Uploading image {i+1} to ImgBB...")
            image_url = self.imgbb_uploader.upload_image(image['path'])
            
            if not image_url:
                print(f"Failed to upload image {i+1}")
                continue
            
            payload = {
                'template': self.bannerbear_template_id,
                'modifications': [
                    {
                        'name': 'image',
                        'image_url': image_url
                    },
                    {
                        'name': 'text',
                        'text': text
                    },
                    {
                        'name': 'slide_number',
                        'text': f"{i+1}/{len(texts)}"
                    }
                ]
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
        
        final_images = []
        for uid in generated_urls:
            final_url = self.wait_for_bannerbear_image(uid)
            if final_url:
                final_images.append(final_url)
        
        return final_images

def main():
    parser = argparse.ArgumentParser(description='Generate Instagram carousels automatically')
    parser.add_argument('--slides', type=int, default=5, help='Number of slides (default: 5)')
    parser.add_argument('--context', type=str, help='Context for carousel copy generation')
    parser.add_argument('--use-imgbb', action='store_true', help='Use ImgBB for image hosting')
    parser.add_argument('--imgbb-key', type=str, help='ImgBB API key (get free at imgbb.com)')
    parser.add_argument('--dry-run', action='store_true', help='Generate copy only, no images')
    
    args = parser.parse_args()
    
    if args.use_imgbb and not args.imgbb_key:
        print("❌ ImgBB API key required when using --use-imgbb")
        print("Get a free API key at: https://api.imgbb.com/")
        sys.exit(1)
    
    try:
        if args.dry_run:
            generator = CarouselGenerator()
            print("🎭 DRY RUN MODE - Generating copy only...")
            texts = generator.generate_carousel_copy(args.context or "")
            print("\n📝 Generated Carousel Copy:")
            for i, text in enumerate(texts):
                print(f"\nSlide {i+1}:\n{text}")
                print("-" * 50)
        else:
            generator = EnhancedCarouselGenerator(
                use_imgbb=args.use_imgbb,
                imgbb_key=args.imgbb_key
            )
            carousel_paths = generator.generate_carousel()
            print("\n🎉 Carousel generation complete!")
            print("📁 Images saved at:")
            for path in carousel_paths:
                print(f"   - {path}")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()