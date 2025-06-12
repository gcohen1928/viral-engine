# Carousel Generator

Automates creating 5-slide carousel posts by:
1. Fetching random images from Google Drive
2. Generating copy with OpenAI Vision API
3. Creating slides with BannerBear templates
4. Saving final images for posting

## Quick Start

```bash
pip install -r requirements.txt
python setup.py
# Fill in your .env file with API keys
python test_components.py  # Test everything works
python carousel_generator.py  # Generate your carousel!
```

## Setup Requirements

### 1. API Keys Needed
- **OpenAI API Key**: From https://platform.openai.com/api-keys
- **BannerBear API Key**: From https://app.bannerbear.com/account/settings
- **BannerBear Template ID**: Create a template with `text_layer` and `image_layer`
- **Google Drive Folder ID**: From the folder URL containing your images

### 2. Google Drive Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project → Enable Google Drive API
3. Create OAuth 2.0 credentials → Download as `credentials.json`
4. Add your email to test users if in testing mode

### 3. BannerBear Template
Create a template with:
- **Text layer** named `text_layer` (or update code)
- **Image layer** named `image_layer` (or update code)
- Copy the template ID from the URL

### 4. Environment Variables
Copy `.env.example` to `.env` and fill in:
```
OPENAI_API_KEY=sk-...
BANNERBEAR_API_KEY=bb_...
BANNERBEAR_TEMPLATE_ID=template_id
GOOGLE_DRIVE_FOLDER_ID=folder_id_from_url
```

## Usage

### Generate Carousel
```bash
python carousel_generator.py
```

### Test Components
```bash
python test_components.py
```

### Customize
- Edit prompt examples in `generate_carousel_copy()`
- Adjust BannerBear layer names in `create_bannerbear_images()`
- Change image count or output directory

## File Structure
```
carousel_generator.py    # Main script
test_components.py      # Test individual APIs
setup.py               # Setup helper
.env                   # Your API keys
credentials.json       # Google OAuth credentials
generated_carousel/    # Output images
```

## Troubleshooting

**Google Drive Auth**: Delete `token.json` and re-authenticate

**BannerBear Layer Names**: Check your template and update layer names in code

**Image Formats**: Ensure Google Drive folder contains valid image files

**Rate Limits**: Script includes 2-second delays between BannerBear requests
