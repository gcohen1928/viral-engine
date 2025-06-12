# 🎨 Carousel Generator

Automate Instagram carousel creation by combining Google Drive images, AI-generated copy, and BannerBear templates.

## Features

- 📸 Fetches random images from Google Drive
- ✍️ Generates engaging carousel copy using OpenAI
- 🖼️ Creates beautiful carousels with BannerBear templates
- 💾 Saves generated images ready for posting

## Quick Start

### 1. Prerequisites

- Python 3.8+
- Google Account with Drive access
- OpenAI API key
- BannerBear account with template

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd carousel-generator

# Install dependencies
pip install -r requirements.txt

# Run setup script
python setup.py
```

### 3. Configuration

#### Google Drive Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Google Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials JSON

#### BannerBear Template
Your template should have these layers:
- `image` - for the background image
- `text` - for the carousel copy
- `slide_number` - for slide numbering (optional)

#### Environment Variables
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_key
BANNERBEAR_API_KEY=your_bannerbear_key
BANNERBEAR_TEMPLATE_ID=your_template_id
GOOGLE_DRIVE_FOLDER_ID=your_folder_id
```

### 4. Usage

#### Basic Usage
```bash
python carousel_generator.py
```

#### CLI with Options
```bash
# Generate 3-slide carousel
python carousel_cli.py --slides 3

# Add context for better copy
python carousel_cli.py --context "fitness tips for beginners"

# Dry run (copy only, no images)
python carousel_cli.py --dry-run

# Use ImgBB for image hosting
python carousel_cli.py --use-imgbb --imgbb-key YOUR_IMGBB_KEY
```

## Advanced Options

### Using ImgBB (Free Image Hosting)
If BannerBear requires public URLs:
1. Get free API key from [ImgBB](https://imgbb.com/)
2. Use CLI with `--use-imgbb` flag

### Custom Templates
Modify `create_bannerbear_images()` to match your template structure:
```python
'modifications': [
    {
        'name': 'your_image_layer',
        'image_url': image_url
    },
    {
        'name': 'your_text_layer', 
        'text': text
    }
]
```

## Troubleshooting

### Google Drive Auth Issues
- Delete `token.json` and re-authenticate
- Check folder permissions in Drive

### BannerBear Issues
- Verify template layer names match code
- Check API key permissions
- Ensure template is active

### OpenAI Issues
- Verify API key has sufficient credits
- Try using `gpt-3.5-turbo` instead of `gpt-4`

## Output Structure
```
generated_carousels/
└── carousel_20240115_123456/
    ├── slide_1.png
    ├── slide_2.png
    ├── slide_3.png
    ├── slide_4.png
    └── slide_5.png
```

## License
MIT
