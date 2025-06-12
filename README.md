# Carousel Generator

Automates creating configurable carousel posts by:
1. Fetching specific images from 5 Google Drive folders
2. Generating copy with OpenAI Vision API using TikTok performance data
3. Creating slides with BannerBear templates
4. Saving final images for posting

## 🎯 Configurable Structure

**Flexible slide count (2-10 slides):**
- **Slide 1**: Always random from `selfies` folder
- **Middle slides**: Random from `legs`, `paths`, or `friends` folders
- **Last slide**: Always random from `leo-screenshots` folder

**Dynamic prompting based on TikTok performance data**

## Quick Start

```bash
pip install -r requirements.txt
python3 setup.py
# Fill in your .env file with API keys and 5 folder IDs
python3 add_tiktok_examples.py  # Add your TikTok performance data
python3 test_components.py      # Test everything works
python3 carousel_generator.py   # Generate your carousel!
```

## Setup Requirements

### 1. Create Google Drive Folders
Create these 5 folders in Google Drive and add images:
- `selfies` (for first slide)
- `legs` (for middle slides)
- `paths` (for middle slides) 
- `friends` (for middle slides)
- `leo-screenshots` (for last slide)

### 2. API Keys Needed
- **OpenAI API Key**: From https://platform.openai.com/api-keys
- **BannerBear API Key**: From https://app.bannerbear.com/account/settings
- **BannerBear Template ID**: Create a template with `text_layer` and `image_layer`
- **5 Google Drive Folder IDs**: From each folder URL

### 3. Google Drive Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project → Enable Google Drive API
3. Create OAuth 2.0 credentials → Download as `credentials.json`
4. Add your email to test users if in testing mode

### 4. BannerBear Template
Create a template with:
- **Text layer** named `text_layer` (or update code)
- **Image layer** named `image_layer` (or update code)
- Copy the template ID from the URL

### 5. Environment Variables
Copy `.env.example` to `.env` and fill in:
```
OPENAI_API_KEY=sk-...
BANNERBEAR_API_KEY=bb_...
BANNERBEAR_TEMPLATE_ID=template_id

SELFIES_FOLDER_ID=folder_id_from_url
LEGS_FOLDER_ID=folder_id_from_url
PATHS_FOLDER_ID=folder_id_from_url
FRIENDS_FOLDER_ID=folder_id_from_url
LEO_SCREENSHOTS_FOLDER_ID=folder_id_from_url
```

### 6. Add TikTok Performance Data
```bash
python3 add_tiktok_examples.py
```
Edit the script to include:
- 8 high-performing TikTok copy examples (5k+ views)
- 3 low-performing TikTok copy examples (<400 views)

This trains the AI to generate high-performing copy.

## Usage

### Generate Carousel
```bash
python3 carousel_generator.py
# Choose slide count (2-10, default 5)
```

### Test Components
```bash
python3 test_components.py
```

### Check Configuration
```bash
python3 config_helper.py
```

### Add TikTok Examples
```bash
python3 add_tiktok_examples.py
```

## Features

### 🔢 Configurable Slide Count
- Choose 2-10 slides
- Dynamic prompt generation for different lengths
- Intelligent folder selection for middle slides

### 📊 TikTok Performance Learning
- Uses your actual TikTok performance data
- Few-shot prompting with high vs low performers
- Learns patterns from successful content

### 🎨 Smart Image Selection
- Always starts with selfie (personal branding)
- Randomly varies middle content (legs/paths/friends)
- Always ends with leo-screenshot (call-to-action)

### 📁 Organized Output
- Creates timestamped folders
- Named by slide count: `5_slides_1234567890/`
- Easy to track different carousel versions

## File Structure
```
carousel_generator.py     # Main configurable script
add_tiktok_examples.py   # TikTok performance data helper
test_components.py       # Test all APIs and features
config_helper.py         # Inspect setup and test generation
setup.py                # Setup helper
.env                     # Your API keys & folder IDs
credentials.json         # Google OAuth credentials
generated_carousel/      # Output images with timestamps
```

## Advanced Customization

### Slide Structure Templates
Edit `generate_dynamic_prompt()` to customize:
- 3-slide: Hook → Value → CTA
- 4-slide: Hook → Problem → Solution → CTA  
- 5-slide: Hook → Problem → Tip #1 → Tip #2 → CTA
- 6+ slides: Hook → Value slides → CTA

### TikTok Learning
The AI analyzes your TikTok performance patterns:
- Successful hooks and structures
- Engagement-driving language
- Call-to-action effectiveness

### Folder Logic
- `selfies`: Personal connection (slide 1)
- `legs/paths/friends`: Varied content (middle)
- `leo-screenshots`: Consistent CTA (last slide)

## Troubleshooting

**Google Drive Auth**: Delete `token.json` and re-authenticate

**Missing Images**: Use `config_helper.py` to check folder contents

**TikTok Examples**: Use `add_tiktok_examples.py` to update performance data

**BannerBear Layer Names**: Use `config_helper.py` to inspect template

**Rate Limits**: Script includes 2-second delays between BannerBear requests
