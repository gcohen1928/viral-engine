#!/usr/bin/env python3
"""
Helper script to add TikTok examples to carousel_generator.py

Just provide the TikTok copy and view counts, and this script will 
format them properly and update the carousel generator.
"""

import re

def format_tiktok_examples(good_examples, bad_examples):
    """Format TikTok examples for insertion into carousel_generator.py"""
    
    print("🎯 Formatting TikTok examples for carousel generator...\n")
    
    # Format good examples
    good_formatted = []
    print("✅ HIGH PERFORMING EXAMPLES (5k+ views):")
    for i, (copy, views) in enumerate(good_examples, 1):
        # Clean the copy text
        clean_copy = copy.strip().replace('"', '\\"')  # Escape quotes
        good_formatted.append(f'            {{"copy": "{clean_copy}", "views": "{views}"}},')
        print(f"   {i}. {copy[:60]}{'...' if len(copy) > 60 else ''} - {views} views")
    
    print(f"\n❌ LOW PERFORMING EXAMPLES (<400 views):")
    bad_formatted = []
    for i, (copy, views) in enumerate(bad_examples, 1):
        # Clean the copy text
        clean_copy = copy.strip().replace('"', '\\"')  # Escape quotes
        bad_formatted.append(f'            {{"copy": "{clean_copy}", "views": "{views}"}},')
        print(f"   {i}. {copy[:60]}{'...' if len(copy) > 60 else ''} - {views} views")
    
    # Generate the replacement code
    replacement_code = f"""        # TikTok examples for few-shot prompting
        self.good_examples = [
            # High performing TikTok examples (5k+ views)
{chr(10).join(good_formatted)}
        ]
        
        self.bad_examples = [
            # Low performing TikTok examples (<400 views)
{chr(10).join(bad_formatted)}
        ]"""
    
    return replacement_code

def update_carousel_generator(replacement_code):
    """Update the carousel_generator.py file with new examples"""
    
    print(f"\n📝 Generated replacement code:")
    print("="*60)
    print(replacement_code)
    print("="*60)
    
    print(f"\n🔧 To update carousel_generator.py:")
    print("1. Open carousel_generator.py") 
    print("2. Find the section with:")
    print("   # TikTok examples for few-shot prompting")
    print("   self.good_examples = [")
    print("3. Replace everything from '# TikTok examples...' down to the end of 'self.bad_examples = [...]'")
    print("4. Paste the code above")
    
    # Optional: Try to auto-update the file
    try:
        with open('carousel_generator.py', 'r') as f:
            content = f.read()
        
        # Find the section to replace
        pattern = r'        # TikTok examples for few-shot prompting.*?        \]'
        
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, replacement_code, content, flags=re.DOTALL)
            
            # Write back
            with open('carousel_generator.py', 'w') as f:
                f.write(new_content)
                
            print("\n✅ Successfully updated carousel_generator.py!")
            
        else:
            print("\n⚠️  Could not auto-update. Please update manually using the code above.")
            
    except Exception as e:
        print(f"\n⚠️  Could not auto-update: {e}")
        print("Please update manually using the code above.")

def main():
    """Main function - add your TikTok examples here"""
    
    print("📱 TikTok Example Formatter")
    print("="*50)
    
    # ADD YOUR TIKTOK EXAMPLES HERE
    # Format: [(copy_text, view_count), ...]
    
    good_examples = [
        # Replace these with your actual high-performing TikToks (5k+ views)
        ("Your first high-performing TikTok copy here", "5.2k"),
        ("Your second high-performing TikTok copy here", "8.1k"), 
        ("Your third high-performing TikTok copy here", "12.5k"),
        ("Your fourth high-performing TikTok copy here", "6.7k"),
        ("Your fifth high-performing TikTok copy here", "9.3k"),
        ("Your sixth high-performing TikTok copy here", "15.2k"),
        ("Your seventh high-performing TikTok copy here", "7.8k"),
        ("Your eighth high-performing TikTok copy here", "11.4k"),
    ]
    
    bad_examples = [
        # Replace these with your actual low-performing TikToks (<400 views)
        ("Your first low-performing TikTok copy here", "245"),
        ("Your second low-performing TikTok copy here", "378"),
        ("Your third low-performing TikTok copy here", "156"),
    ]
    
    # Check if examples are still placeholders
    if any("Your" in copy for copy, _ in good_examples + bad_examples):
        print("🚨 PLEASE UPDATE THE EXAMPLES ABOVE!")
        print("\nReplace the placeholder text with your actual TikTok copy and view counts.")
        print("\nExample format:")
        print('("POV: you discover the secret to viral content", "15.2k"),')
        return
    
    # Format and update
    replacement_code = format_tiktok_examples(good_examples, bad_examples)
    update_carousel_generator(replacement_code)

if __name__ == "__main__":
    main()

# QUICK USAGE:
# 1. Replace the examples in good_examples and bad_examples above
# 2. Run: python3 add_tiktok_examples.py
# 3. Your carousel generator will be updated with real examples!