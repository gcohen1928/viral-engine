#!/usr/bin/env python3
"""
Example usage of the Carousel Generator
"""

from carousel_generator import CarouselGenerator
from carousel_cli import EnhancedCarouselGenerator

def example_basic():
    """Basic usage example"""
    print("=== Basic Carousel Generation ===")
    generator = CarouselGenerator()
    carousel_paths = generator.generate_carousel()
    print(f"Generated {len(carousel_paths)} carousel slides")

def example_with_context():
    """Generate carousel with specific context"""
    print("\n=== Carousel with Context ===")
    generator = CarouselGenerator()
    
    # Generate copy for specific context
    context = "productivity tips for remote workers"
    carousel_texts = generator.generate_carousel_copy(context)
    
    print("Generated copy:")
    for i, text in enumerate(carousel_texts):
        print(f"Slide {i+1}: {text}")
    
    # Continue with image generation...
    images = generator.get_random_images(5)
    image_urls = generator.create_bannerbear_images(images, carousel_texts)
    local_paths = generator.download_final_images(image_urls)
    
    return local_paths

def example_custom_slides():
    """Generate carousel with custom number of slides"""
    print("\n=== Custom Slide Count ===")
    generator = CarouselGenerator()
    
    # Override the default slide count
    slide_count = 3
    images = generator.get_random_images(slide_count)
    
    # Modify the prompt for 3 slides
    prompt = """Generate engaging copy for a 3-slide Instagram carousel.
    Slide 1: Hook
    Slide 2: Main value
    Slide 3: CTA
    Keep each under 30 words. Return ONLY 3 slide texts, one per line."""
    
    # Custom OpenAI call
    response = generator.openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a social media copywriting expert."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8
    )
    
    carousel_texts = response.choices[0].message.content.strip().split('\n')[:3]
    
    # Generate images
    image_urls = generator.create_bannerbear_images(images, carousel_texts)
    local_paths = generator.download_final_images(image_urls)
    
    return local_paths

def example_batch_generation():
    """Generate multiple carousels in batch"""
    print("\n=== Batch Generation ===")
    generator = CarouselGenerator()
    
    contexts = [
        "morning routine tips",
        "healthy eating habits",
        "workout motivation"
    ]
    
    all_carousels = []
    
    for context in contexts:
        print(f"\nGenerating carousel for: {context}")
        try:
            # Generate copy
            texts = generator.generate_carousel_copy(context)
            
            # Get images
            images = generator.get_random_images(5)
            
            # Create carousel
            image_urls = generator.create_bannerbear_images(images, texts)
            local_paths = generator.download_final_images(image_urls)
            
            all_carousels.append({
                'context': context,
                'paths': local_paths,
                'texts': texts
            })
            
            # Cleanup temp files
            for image in images:
                import os
                os.remove(image['path'])
                
        except Exception as e:
            print(f"Failed to generate carousel for {context}: {e}")
    
    return all_carousels

def example_with_imgbb():
    """Example using ImgBB for image hosting"""
    print("\n=== Using ImgBB Image Hosting ===")
    
    # You need to set IMGBB_API_KEY in environment or pass it directly
    imgbb_key = "your_imgbb_api_key_here"
    
    generator = EnhancedCarouselGenerator(
        use_imgbb=True,
        imgbb_key=imgbb_key
    )
    
    carousel_paths = generator.generate_carousel()
    print(f"Generated carousel with ImgBB hosting")
    
    return carousel_paths

if __name__ == "__main__":
    # Run examples
    try:
        # Basic example
        example_basic()
        
        # With context
        example_with_context()
        
        # Custom slides
        example_custom_slides()
        
        # Batch generation
        results = example_batch_generation()
        print(f"\nGenerated {len(results)} carousels in batch")
        
    except Exception as e:
        print(f"Error in examples: {e}")
        print("\nMake sure you have:")
        print("1. Set up your .env file with all API keys")
        print("2. Configured Google Drive OAuth")
        print("3. Created BannerBear template with correct layer names")