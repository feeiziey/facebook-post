#!/usr/bin/env python3
"""
Multi-Provider Image Generation Script for Facebook Posts
Processes waiting picture posts from Notion and generates images using various AI services
"""

import os
import requests
import time
import base64
from datetime import datetime

# Configuration
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_BANK_DB_ID = '229bc30eae8c803bac1be32cc42ee186'  # Correct database ID
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', 'feeiziey/facebook-post')

# Multiple model options
HF_MODEL_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
STABLE_HORDE_URL = "https://stablehorde.net/api/v2/generate/async"
REPLICATE_URL = "https://api.replicate.com/v1/predictions"

# Headers for Notion API
notion_headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

# Headers for Hugging Face API
hf_headers = {
    'Authorization': f'Bearer {HUGGINGFACE_TOKEN}',
    'Content-Type': 'application/json'
}

DEEPAI_API_KEY = os.environ.get('DEEPAI_API_KEY')

def get_waiting_picture_posts():
    """Get all waiting picture posts from Notion"""
    print("🔍 Searching for waiting picture posts...")
    
    query_data = {
        'filter': {
            'and': [
                {
                    'property': 'Status',
                    'rich_text': {
                        'contains': 'Waiting'
                    }
                },
                {
                    'property': 'Content',
                    'rich_text': {
                        'contains': 'Picture'
                    }
                }
            ]
        }
    }
    
    response = requests.post(
        f'https://api.notion.com/v1/databases/{NOTION_BANK_DB_ID}/query',
        headers=notion_headers,
        json=query_data
    )
    
    if response.status_code == 200:
        data = response.json()
        posts = []
        for record in data['results']:
            # Extract properties
            prompt_prop = record['properties'].get('Prompt', {})
            caption_prop = record['properties'].get('Caption', {})
            prompt = prompt_prop['title'][0]['text']['content'] if prompt_prop.get('title') else ''
            caption = caption_prop['rich_text'][0]['text']['content'] if caption_prop.get('rich_text') else ''
            # Only process if we have a prompt
            if prompt:
                posts.append({
                    'id': record['id'],
                    'prompt': prompt,
                    'caption': caption
                })
        
        print(f"📋 Found {len(posts)} waiting picture posts")
        return posts
    else:
        print(f"❌ Error querying Notion: {response.status_code} - {response.text}")
        return []

def generate_image_with_free_api(caption):
    """Generate a quote-style image with the caption and a 'Daily Wonderwise' tag."""
    print(f"🎨 Generating quote-style fallback image: {caption[:50]}...")
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io
        import os
        import requests
        # Image settings
        width, height = 1024, 1024
        bg_color = '#111111'
        text_color = '#FFFFFF'
        tag_color = '#FFFFFF'
        accent_color = '#F5C242'  # Gold accent for the line
        font_size = 80
        tag_font_size = 28
        margin = 80  # Increased margin for better padding
        line_spacing = 24
        # Ensure fonts directory exists
        font_dir = os.path.join(os.path.dirname(__file__), 'fonts')
        os.makedirs(font_dir, exist_ok=True)
        font_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
        # Download font if not present
        if not os.path.exists(font_path):
            print(f"⬇️  Downloading DejaVuSans-Bold.ttf to {font_path} ...")
            url = "https://github.com/dejavu-fonts/dejavu-fonts/raw/master/ttf/DejaVuSans-Bold.ttf"
            r = requests.get(url)
            with open(font_path, 'wb') as f:
                f.write(r.content)
        # Load font
        font = ImageFont.truetype(font_path, font_size)
        tag_font = ImageFont.truetype(font_path, tag_font_size)
        print(f"✅ Using font: {font_path}")
        # Create image and draw object
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)
        # Word wrap caption
        def text_width_height(text, font):
            bbox = font.getbbox(text)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            return w, h
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            line = ''
            for word in words:
                test_line = f'{line} {word}'.strip()
                w, _ = text_width_height(test_line, font)
                if w <= max_width:
                    line = test_line
                else:
                    lines.append(line)
                    line = word
            if line:
                lines.append(line)
            return lines
        quote_lines = wrap_text(caption, font, width - 2 * margin)
        # Calculate text height
        _, line_height = text_width_height('A', font)
        line_height += line_spacing
        total_text_height = line_height * len(quote_lines)
        # Draw caption text centered
        y = (height - total_text_height) // 2
        for line in quote_lines:
            w, _ = text_width_height(line, font)
            x = (width - w) // 2
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_height
        # Draw accent line above tag
        tag_y = height - margin - tag_font_size - 30
        line_width = 80
        line_x = (width - line_width) // 2
        draw.line([(line_x, tag_y), (line_x + line_width, tag_y)], fill=accent_color, width=4)
        # Draw tag text
        tag_text = "DAILY WONDERWISE"
        tag_w, tag_h = text_width_height(tag_text, tag_font)
        tag_x = (width - tag_w) // 2
        draw.text((tag_x, tag_y + 16), tag_text, fill=tag_color, font=tag_font)
        # Save to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        print("✅ Quote-style fallback image created successfully")
        return img_byte_arr
    except ImportError:
        print("❌ PIL not available, cannot create quote-style fallback image")
        return None
    except Exception as e:
        print(f"❌ Error creating quote-style fallback image: {e}")
        return None

def generate_image_with_huggingface(prompt):
    """Generate image using FLUX.1-schnell - Much better quality than Stable Diffusion XL"""
    print(f"🎨 Generating high-quality image with FLUX.1-schnell: {prompt[:50]}...")
    
    # FLUX.1-schnell optimized parameters for best quality
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 4,  # FLUX.1-schnell is optimized for 1-4 steps
            "guidance_scale": 0.0,     # FLUX.1-schnell doesn't need guidance
            "width": 1024,
            "height": 1024,
            "max_sequence_length": 256  # Optimized for FLUX
        }
    }
    
    try:
        response = requests.post(
            HF_MODEL_URL,
            headers=hf_headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ High-quality image generated successfully with FLUX.1-schnell!")
            return response.content
        elif response.status_code == 503:
            # Model is loading, wait and retry
            print("⏳ FLUX.1-schnell model is loading, waiting 20 seconds...")
            time.sleep(20)
            return generate_image_with_huggingface(prompt)
        elif response.status_code == 402:
            print("❌ Hugging Face credits exceeded, trying alternative...")
            return None
        else:
            print(f"❌ Error generating image: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def generate_image_with_deepai(prompt):
    """Generate image using DeepAI text2img API"""
    print(f"🎨 Generating image with DeepAI: {prompt[:50]}...")
    if not DEEPAI_API_KEY:
        print("❌ DeepAI API key not set. Skipping DeepAI fallback.")
        return None
    try:
        response = requests.post(
            "https://api.deepai.org/api/text2img",
            data={'text': prompt},
            headers={'api-key': DEEPAI_API_KEY},
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            image_url = result.get('output_url')
            if image_url:
                img_response = requests.get(image_url, timeout=60)
                if img_response.status_code == 200:
                    print("✅ Image generated successfully with DeepAI!")
                    return img_response.content
                else:
                    print(f"❌ Failed to download DeepAI image: {img_response.status_code}")
            else:
                print(f"❌ DeepAI did not return an image URL: {result}")
        else:
            print(f"❌ Error from DeepAI: {response.status_code} - {response.text}")
        return None
    except Exception as e:
        print(f"❌ Error with DeepAI: {e}")
        return None

# Update fallback logic to accept both prompt and caption
def generate_image_with_fallback(prompt, caption=None):
    """Try Hugging Face, then fallback to quote-style image using caption if available."""
    print(f"🎨 Attempting image generation for: {prompt[:50]}...")
    # Try Hugging Face first (if credits available)
    if HUGGINGFACE_TOKEN:
        print("🔄 Trying Hugging Face FLUX.1-schnell...")
        image_data = generate_image_with_huggingface(prompt)
        if image_data:
            return image_data, "FLUX.1-schnell"
    # Fallback to quote-style image using caption if provided, else prompt
    print("🔄 All real image APIs unavailable, generating quote-style fallback image...")
    image_data = generate_image_with_free_api(caption if caption else prompt)
    if image_data:
        return image_data, "Free API"
    print("❌ All image generation services failed")
    return None, None

def save_image_locally(image_data, filename):
    """Save image data to local file and return GitHub URL"""
    print(f"💾 Saving image locally: {filename}")
    
    # Create images directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Save locally
    local_path = f'images/{filename}'
    with open(local_path, 'wb') as f:
        f.write(image_data)
    
    # Return the GitHub URL where the image will be accessible
    github_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/main/images/{filename}'
    print(f"✅ Image saved locally and will be available at: {github_url}")
    return github_url

def commit_and_push_image(filename, prompt):
    """Commit and push a single image to GitHub immediately"""
    print(f"💾 Committing and pushing image: {filename}")
    
    try:
        import subprocess
        
        # Configure git
        subprocess.run(['git', 'config', '--local', 'user.email', 'action@github.com'], check=True)
        subprocess.run(['git', 'config', '--local', 'user.name', 'GitHub Action'], check=True)
        
        # Add the specific image file
        subprocess.run(['git', 'add', f'images/{filename}'], check=True)
        
        # Commit with descriptive message
        commit_message = f"Add generated image: {filename[:30]}... - {prompt[:50]}..."
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to repository
        subprocess.run(['git', 'push'], check=True)
        
        print(f"✅ Successfully committed and pushed: {filename}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error committing image {filename}: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error committing image {filename}: {e}")
        return False

def update_notion_record_with_image_and_status(record_id, image_url):
    """Update Notion record with the generated image link and change status to Pending"""
    print(f"📝 Updating Notion record with image link and changing status to Pending...")
    
    update_data = {
        'properties': {
            'Link': {
                'rich_text': [
                    {
                        'text': {
                            'content': image_url
                        }
                    }
                ]
            },
            'Status': {
                'rich_text': [
                    {
                        'text': {
                            'content': 'Pending'
                        }
                    }
                ]
            }
        }
    }
    
    response = requests.patch(
        f'https://api.notion.com/v1/pages/{record_id}',
        headers=notion_headers,
        json=update_data
    )
    
    if response.status_code == 200:
        print("✅ Notion record updated successfully - Status changed to Pending")
        return True
    else:
        print(f"❌ Error updating Notion: {response.status_code} - {response.text}")
        return False

def main():
    """Main execution function"""
    print("🚀 Starting Facebook Post Image Generation with Multi-Provider Fallback")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN environment variable not set")
        return
    
    # Get waiting picture posts
    posts = get_waiting_picture_posts()
    
    if not posts:
        print("✅ No waiting picture posts found")
        return
    
    # Process each post
    for i, post in enumerate(posts, 1):
        print(f"\n📸 Processing post {i}/{len(posts)}")
        print(f"Prompt: {post['prompt']}")
        
        # Generate image with fallback system
        image_data, model_used = generate_image_with_fallback(post['prompt'], post.get('caption', post['prompt']))
        if not image_data:
            print(f"⏭️ Skipping post {i} due to generation error")
            continue
        
        # Generate filename based on model used
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if model_used == "FLUX.1-schnell":
            filename = f'flux_generated_{timestamp}_{i}.png'
        elif model_used == "Free API":
            filename = f'freeapi_generated_{timestamp}_{i}.png'
        else:
            filename = f'quote_generated_{timestamp}_{i}.png' # Changed filename for quote-style
        
        # Save image locally and get GitHub URL
        github_url = save_image_locally(image_data, filename)
        if not github_url:
            continue
        
        # Update Notion record with image link and change status to Pending
        update_notion_record_with_image_and_status(post['id'], github_url)
        
        # Commit and push the image immediately
        commit_and_push_image(filename, post['prompt'])
        
        print(f"✅ Successfully processed post {i} with {model_used}")
        
        # Add a small delay between requests to be respectful to the API
        if i < len(posts):
            print("⏳ Waiting 5 seconds before next request...")
            time.sleep(5)
    
    print(f"\n🎯 Completed processing {len(posts)} posts with multi-provider fallback")

if __name__ == '__main__':
    main() 