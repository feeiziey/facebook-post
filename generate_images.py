#!/usr/bin/env python3
"""
Hugging Face Image Generation Script for Facebook Posts
Processes waiting picture posts from Notion and generates images using Hugging Face Inference API
"""

import os
import requests
import time
from datetime import datetime

# Configuration
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_BANK_DB_ID = '229bc30eae8c803bac1be32cc42ee186'  # Correct database ID
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', 'feeiziey/facebook-post')

# Use FLUX.1-schnell - Much better quality and faster than Stable Diffusion XL
HF_MODEL_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"

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
            
            prompt = prompt_prop['title'][0]['text']['content'] if prompt_prop.get('title') else ''
            
            # Only process if we have a prompt
            if prompt:
                posts.append({
                    'id': record['id'],
                    'prompt': prompt
                })
        
        print(f"📋 Found {len(posts)} waiting picture posts")
        return posts
    else:
        print(f"❌ Error querying Notion: {response.status_code} - {response.text}")
        return []

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
        else:
            print(f"❌ Error generating image: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

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
    print("🚀 Starting Facebook Post Image Generation with FLUX.1-schnell")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN environment variable not set")
        return
    
    if not HUGGINGFACE_TOKEN:
        print("❌ HUGGINGFACE_TOKEN environment variable not set")
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
        
        # Generate image with FLUX.1-schnell (much better quality)
        image_data = generate_image_with_huggingface(post['prompt'])
        if not image_data:
            print(f"⏭️ Skipping post {i} due to generation error")
            continue
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'flux_generated_{timestamp}_{i}.png'
        
        # Save image locally and get GitHub URL
        github_url = save_image_locally(image_data, filename)
        if not github_url:
            continue
        
        # Update Notion record with image link and change status to Pending
        update_notion_record_with_image_and_status(post['id'], github_url)
        
        print(f"✅ Successfully processed post {i}")
        
        # Add a small delay between requests to be respectful to the API
        if i < len(posts):
            print("⏳ Waiting 5 seconds before next request...")
            time.sleep(5)
    
    print(f"\n🎯 Completed processing {len(posts)} posts with FLUX.1-schnell")

if __name__ == '__main__':
    main() 