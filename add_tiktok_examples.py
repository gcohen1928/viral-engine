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
    
    # Real TikTok examples based on performance data
    
    good_examples = [
        # High performing TikToks (5k+ views)
        ("POV: you're trying to become that girl", "11.8k"),
        ("This is the dumbest way to be a consistent runner but it worked", "7.9k"), 
        ("How to become a running girlie (step by step)", "7.2k"),
        ("I never thought I'd be a runner. i hated cardio and thought it was dumb", "5.2k"),
        ("I got into running for the dumbest reason", "5.2k"),
        ("POV: you're trying to become that girl", "3.3k"),
        ("POV: you gaslit yourself into running", "1.8k"),
        ("i bought a matching set and brooks after my first run. i felt like being financially tied to the sport will motivate me to keep running", "1.8k"),
    ]
    
    bad_examples = [
        # Low performing TikToks (<400 views)
        ("POV: you're becoming a running girlie", "308"),
        ("Why is every run just me not trying to fall apart?? Anyone else??", "350"),
        ("Here's how running saved our relationship (1/5)", "276"),
    ]
    
    print("🎯 Using your real TikTok performance data!")
    print(f"✅ {len(good_examples)} high-performing examples")
    print(f"❌ {len(bad_examples)} low-performing examples")
    
    # Format and update
    replacement_code = format_tiktok_examples(good_examples, bad_examples)
    update_carousel_generator(replacement_code)

if __name__ == "__main__":
    main()

# USAGE:
# This script now contains your real TikTok performance data!
# Just run: python3 add_tiktok_examples.py