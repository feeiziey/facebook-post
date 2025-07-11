#!/usr/bin/env python3
"""
Hugging Face Image Generation Script for Facebook Posts
Processes pending picture posts from Notion and generates images using Hugging Face Inference API
"""

import os
import requests
import json
import time
import base64
from datetime import datetime
from io import BytesIO

# Configuration
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_BANK_DB_ID = '229bc30eae8c803bac1be32cc42ee186'  # Correct database ID
HUGGINGFACE_TOKEN = os.environ.get('HUGGINGFACE_TOKEN')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# GitHub repository info (auto-detect from environment)
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', 'feeiziey/facebook-post')

# Hugging Face model endpoint
HF_MODEL_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"

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

def get_pending_picture_posts():
    """Get all pending picture posts from Notion"""
    print("🔍 Searching for pending picture posts...")
    
    query_data = {
        'filter': {
            'and': [
                {
                    'property': 'Status',
                    'rich_text': {
                        'contains': 'Pending'
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
            link_prop = record['properties'].get('Link', {})
            
            prompt = prompt_prop['title'][0]['text']['content'] if prompt_prop.get('title') else ''
            caption = caption_prop['rich_text'][0]['text']['content'] if caption_prop.get('rich_text') else ''
            link = link_prop['rich_text'][0]['text']['content'] if link_prop.get('rich_text') else ''
            
            # Only process if we have a prompt and no existing link (or empty link)
            if prompt and (not link or link.strip() == ''):
                posts.append({
                    'id': record['id'],
                    'prompt': prompt,
                    'caption': caption
                })
        
        print(f"📋 Found {len(posts)} pending picture posts without links")
        return posts
    else:
        print(f"❌ Error querying Notion: {response.status_code} - {response.text}")
        return []

def generate_image_with_huggingface(prompt):
    """Generate image using Hugging Face Inference API"""
    print(f"🎨 Generating image with Hugging Face: {prompt[:50]}...")
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "num_inference_steps": 30,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 1024
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
            print("✅ Image generated successfully!")
            return response.content
        elif response.status_code == 503:
            # Model is loading, wait and retry
            print("⏳ Model is loading, waiting 20 seconds...")
            time.sleep(20)
            return generate_image_with_huggingface(prompt)
        else:
            print(f"❌ Error generating image: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error to Hugging Face: {e}")
        return None
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout connecting to Hugging Face: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
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
    github_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/master/images/{filename}'
    print(f"✅ Image saved locally and will be available at: {github_url}")
    return github_url

def update_notion_record(record_id, image_url):
    """Update Notion record with the generated image link"""
    print(f"📝 Updating Notion record with image link...")
    
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
            }
        }
    }
    
    response = requests.patch(
        f'https://api.notion.com/v1/pages/{record_id}',
        headers=notion_headers,
        json=update_data
    )
    
    if response.status_code == 200:
        print("✅ Notion record updated successfully")
        return True
    else:
        print(f"❌ Error updating Notion: {response.status_code} - {response.text}")
        return False

def test_connectivity():
    """Test connectivity to Hugging Face API"""
    try:
        # Test with a simple request
        test_payload = {"inputs": "test"}
        response = requests.post(HF_MODEL_URL, headers=hf_headers, json=test_payload, timeout=10)
        if response.status_code in [200, 503]:  # 503 means model is loading, which is fine
            print("✅ Hugging Face API is accessible")
            return True
        else:
            print(f"⚠️ Hugging Face API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach Hugging Face API: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Starting Hugging Face Image Generation Process")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN environment variable not set")
        return
    
    if not HUGGINGFACE_TOKEN:
        print("❌ HUGGINGFACE_TOKEN environment variable not set")
        return
    
    # Test connectivity first
    if not test_connectivity():
        print("🔄 Hugging Face API is not accessible. This might be temporary.")
        print("📋 Will still check for pending posts and exit gracefully.")
    
    # Get pending picture posts
    posts = get_pending_picture_posts()
    
    if not posts:
        print("✅ No pending picture posts found")
        return
    
    # Process each post
    for i, post in enumerate(posts, 1):
        print(f"\n📸 Processing post {i}/{len(posts)}")
        print(f"Caption: {post['caption']}")
        print(f"Prompt: {post['prompt']}")
        
        # Generate image with Hugging Face
        image_data = generate_image_with_huggingface(post['prompt'])
        if not image_data:
            print(f"⏭️ Skipping post {i} due to generation error")
            continue
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'generated_{timestamp}_{i}.png'
        
        # Save image locally and get GitHub URL
        github_url = save_image_locally(image_data, filename)
        if not github_url:
            continue
        
        # Update Notion record
        update_notion_record(post['id'], github_url)
        
        print(f"✅ Successfully processed post {i}")
        
        # Add a small delay between requests to be respectful to the API
        if i < len(posts):
            print("⏳ Waiting 5 seconds before next request...")
            time.sleep(5)
    
    print(f"\n🎯 Completed processing {len(posts)} posts")

if __name__ == '__main__':
    main() 