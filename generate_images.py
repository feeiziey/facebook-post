#!/usr/bin/env python3
"""
Stable Horde Image Generation Script for Facebook Posts
Processes pending picture posts from Notion and generates images using Stable Horde API
"""

import os
import requests
import json
import time
import base64
from datetime import datetime

# Configuration
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_BANK_DB_ID = '229bc30eae8c803bac1be32cc42ee186'  # Correct database ID
STABLE_HORDE_API_KEY = os.environ.get('STABLE_HORDE_API_KEY', '1M0A2GKu0dWMXpVB0ah9gw')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# GitHub repository info (auto-detect from environment)
GITHUB_REPO = os.environ.get('GITHUB_REPOSITORY', 'feeiziey/facebook-post')

# Headers for Notion API
notion_headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

# Headers for Stable Horde API
horde_headers = {
    'apikey': STABLE_HORDE_API_KEY,
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
            link = link_prop.get('select', {}).get('name', '') if link_prop.get('select') else ''
            
            # Only process if we have a prompt and no existing link
            if prompt and not link:
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

def submit_to_stable_horde(prompt):
    """Submit image generation request to Stable Horde"""
    print(f"🎨 Submitting to Stable Horde: {prompt[:50]}...")
    
    payload = {
        "prompt": prompt,
        "params": {
            "width": 512,
            "height": 512,
            "steps": 30,
            "cfg_scale": 7.5,
            "sampler_name": "k_euler_a"
        },
        "nsfw": False,
        "trusted_workers": True,
        "models": ["stable_diffusion"]
    }
    
    try:
        response = requests.post(
            'https://stablehorde.ai/api/v2/generate/async',
            headers=horde_headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 202:
            data = response.json()
            request_id = data['id']
            print(f"✅ Request submitted with ID: {request_id}")
            return request_id
        else:
            print(f"❌ Error submitting to Stable Horde: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error to Stable Horde: {e}")
        print("🔄 This might be a temporary network issue. Will retry later.")
        return None
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout connecting to Stable Horde: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def check_generation_status(request_id):
    """Check the status of image generation"""
    try:
        response = requests.get(
            f'https://stablehorde.ai/api/v2/generate/check/{request_id}',
            headers=horde_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ Error checking status: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error checking status: {e}")
        return None
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return None

def get_generated_image(request_id):
    """Get the generated image from Stable Horde"""
    try:
        response = requests.get(
            f'https://stablehorde.ai/api/v2/generate/status/{request_id}',
            headers=horde_headers,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('done') and data.get('generations'):
                image_url = data['generations'][0]['img']
                print(f"🖼️ Image ready: {image_url}")
                return image_url
            return None
        else:
            print(f"❌ Error getting image: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error getting image: {e}")
        return None
    except Exception as e:
        print(f"❌ Error getting image: {e}")
        return None

def upload_image_to_github(image_url, filename):
    """Download image and upload to GitHub repository"""
    print(f"📤 Uploading image to GitHub: {filename}")
    
    # Download image
    img_response = requests.get(image_url)
    if img_response.status_code != 200:
        print(f"❌ Failed to download image from {image_url}")
        return None
    
    # Encode image as base64
    image_content = base64.b64encode(img_response.content).decode('utf-8')
    
    # Create images directory if it doesn't exist
    os.makedirs('images', exist_ok=True)
    
    # Save locally first
    local_path = f'images/{filename}'
    with open(local_path, 'wb') as f:
        f.write(img_response.content)
    
    # Return the GitHub URL where the image will be accessible
    github_url = f'https://raw.githubusercontent.com/{GITHUB_REPO}/master/images/{filename}'
    print(f"✅ Image will be available at: {github_url}")
    return github_url

def update_notion_record(record_id, image_url):
    """Update Notion record with the generated image link"""
    print(f"📝 Updating Notion record with image link...")
    
    update_data = {
        'properties': {
            'Link': {
                'select': {
                    'name': image_url
                }
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
    """Test connectivity to Stable Horde API"""
    try:
        response = requests.get('https://stablehorde.ai/api/v2/status/heartbeat', timeout=10)
        if response.status_code == 200:
            print("✅ Stable Horde API is accessible")
            return True
        else:
            print(f"⚠️ Stable Horde API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot reach Stable Horde API: {e}")
        return False

def main():
    """Main execution function"""
    print("🚀 Starting Stable Horde Image Generation Process")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN environment variable not set")
        return
    
    # Test connectivity first
    if not test_connectivity():
        print("🔄 Stable Horde API is not accessible. This might be temporary.")
        print("📋 Will still check for pending posts and exit gracefully.")
        # Don't return here - still check Notion to show what posts are pending
    
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
        
        # Submit to Stable Horde
        request_id = submit_to_stable_horde(post['prompt'])
        if not request_id:
            print(f"⏭️ Skipping post {i} due to submission error")
            continue
        
        # Poll for completion (max 10 minutes)
        print("⏳ Waiting for image generation...")
        max_wait = 600  # 10 minutes
        wait_time = 0
        
        while wait_time < max_wait:
            status = check_generation_status(request_id)
            if status:
                if status.get('done'):
                    print("🎉 Image generation completed!")
                    break
                else:
                    queue_position = status.get('queue_position', 'unknown')
                    wait_time_left = status.get('wait_time', 'unknown')
                    print(f"⏳ Queue position: {queue_position}, Wait time: {wait_time_left}s")
            
            time.sleep(30)  # Check every 30 seconds
            wait_time += 30
        
        if wait_time >= max_wait:
            print("⏰ Timeout waiting for image generation")
            continue
        
        # Get the generated image
        image_url = get_generated_image(request_id)
        if not image_url:
            continue
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'generated_{timestamp}_{i}.png'
        
        # Upload to GitHub
        github_url = upload_image_to_github(image_url, filename)
        if not github_url:
            continue
        
        # Update Notion record
        update_notion_record(post['id'], github_url)
        
        print(f"✅ Successfully processed post {i}")
    
    print(f"\n🎯 Completed processing {len(posts)} posts")

if __name__ == '__main__':
    main() 