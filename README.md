# Carousel Generator

Automates creating 5-slide carousel posts by:
1. Fetching specific images from 5 Google Drive folders
2. Generating copy with OpenAI Vision API 
3. Creating slides with BannerBear templates
4. Saving final images for posting

## 🎯 Folder Structure

Each slide uses a specific image type:
- **Slide 1**: Random image from `selfies` folder
- **Slide 2**: Random image from `legs` folder  
- **Slide 3**: Random image from `paths` folder
- **Slide 4**: Random image from `friends` folder
- **Slide 5**: Random image from `leo-screenshots` folder

## Quick Start

```bash
pip install -r requirements.txt
python3 setup.py
# Fill in your .env file with API keys and 5 folder IDs
python3 test_components.py  # Test everything works
python3 carousel_generator.py  # Generate your carousel!
```

## Setup Requirements

### 1. Create Google Drive Folders
Create these 5 folders in Google Drive and add images:
- `selfies` 
- `legs`
- `paths` 
- `friends`
- `leo-screenshots`

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

## Usage

### Generate Carousel
```bash
python3 carousel_generator.py
```

### Test Components
```bash
python3 test_components.py
```

### Check Configuration
```bash
python3 config_helper.py
```

### Customize
- Edit prompt examples in `generate_carousel_copy()`
- Adjust BannerBear layer names in `create_bannerbear_images()`
- Change folder names by updating the script

## File Structure
```
carousel_generator.py    # Main script
test_components.py      # Test individual APIs
config_helper.py        # Inspect setup
setup.py               # Setup helper
.env                   # Your API keys & folder IDs
credentials.json       # Google OAuth credentials
generated_carousel/    # Output images
```

## Troubleshooting

**Google Drive Auth**: Delete `token.json` and re-authenticate

**Missing Images**: Use `config_helper.py` to check folder contents

**BannerBear Layer Names**: Use `config_helper.py` to inspect template

**Rate Limits**: Script includes 2-second delays between BannerBear requests
