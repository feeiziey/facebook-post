#!/usr/bin/env python3
"""
Bulk Content Importer for Facebook Posts
Imports content from ChatGPT or other sources and adds to Notion database
"""

import os
import requests
import json
import re
from datetime import datetime

# Configuration
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_BANK_DB_ID = '229bc30eae8c803bac1be32cc42ee186'  # Your bank database ID

# Headers for Notion API
notion_headers = {
    'Authorization': f'Bearer {NOTION_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def parse_chatgpt_content(content):
    """
    Parse ChatGPT-generated content and extract structured data
    Supports various formats like:
    1. Post Title | Caption | Prompt | Type
    2. Numbered lists with different sections
    3. Markdown tables
    """
    
    posts = []
    lines = content.strip().split('\n')
    
    # Method 1: Try to parse as table format (pipe-separated)
    if '|' in content:
        print("🔍 Detected table format...")
        for line in lines:
            if '|' in line and not line.strip().startswith('|---'):
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4:
                    # Skip header row
                    if parts[0].lower() in ['post', 'title', 'caption', 'content']:
                        continue
                    
                    post_data = {
                        'title': parts[0],
                        'caption': parts[1] if len(parts) > 1 else '',
                        'prompt': parts[2] if len(parts) > 2 else '',
                        'type': parts[3].lower() if len(parts) > 3 else 'text'
                    }
                    
                    # Determine if it's a picture or text post
                    if 'picture' in post_data['type'] or post_data['prompt']:
                        post_data['content_type'] = 'Picture'
                    else:
                        post_data['content_type'] = 'Text'
                    
                    posts.append(post_data)
    
    # Method 2: Try to parse numbered lists
    elif re.search(r'^\d+\.', content, re.MULTILINE):
        print("🔍 Detected numbered list format...")
        current_post = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a numbered item
            if re.match(r'^\d+\.', line):
                # Save previous post if exists
                if current_post:
                    posts.append(current_post)
                
                # Start new post
                current_post = {
                    'title': re.sub(r'^\d+\.\s*', '', line),
                    'caption': '',
                    'prompt': '',
                    'type': 'text',
                    'content_type': 'Text'
                }
            
            # Look for specific keywords
            elif 'caption:' in line.lower():
                current_post['caption'] = line.split(':', 1)[1].strip()
            elif 'prompt:' in line.lower():
                current_post['prompt'] = line.split(':', 1)[1].strip()
                current_post['content_type'] = 'Picture'
            elif 'type:' in line.lower():
                post_type = line.split(':', 1)[1].strip().lower()
                current_post['type'] = post_type
                if 'picture' in post_type:
                    current_post['content_type'] = 'Picture'
        
        # Add the last post
        if current_post:
            posts.append(current_post)
    
    # Method 3: Simple line-by-line parsing
    else:
        print("🔍 Detected simple text format...")
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:  # Ignore very short lines
                posts.append({
                    'title': line,
                    'caption': '',
                    'prompt': '',
                    'type': 'text',
                    'content_type': 'Text'
                })
    
    return posts

def add_post_to_notion(post_data):
    """Add a single post to Notion database"""
    
    # Determine the main content (title or caption)
    main_content = post_data.get('title', '') or post_data.get('caption', '')
    
    if post_data['content_type'] == 'Picture':
        # Picture post
        page_properties = {
            'Name': {  # Main title property
                'title': [
                    {
                        'text': {
                            'content': main_content
                        }
                    }
                ]
            },
            'Status': {
                'rich_text': [
                    {
                        'text': {
                            'content': 'Waiting'
                        }
                    }
                ]
            },
            'Content': {
                'rich_text': [
                    {
                        'text': {
                            'content': 'Picture'
                        }
                    }
                ]
            },
            'Prompt': {
                'rich_text': [
                    {
                        'text': {
                            'content': post_data.get('prompt', '')
                        }
                    }
                ]
            }
        }
    else:
        # Text post
        page_properties = {
            'Name': {  # Main title property
                'title': [
                    {
                        'text': {
                            'content': main_content
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
            },
            'Content': {
                'rich_text': [
                    {
                        'text': {
                            'content': 'Text'
                        }
                    }
                ]
            }
        }
    
    # Create the page
    response = requests.post(
        'https://api.notion.com/v1/pages',
        headers=notion_headers,
        json={
            'parent': {
                'database_id': NOTION_BANK_DB_ID
            },
            'properties': page_properties
        }
    )
    
    return response.status_code == 200

def main():
    """Main function to import bulk content"""
    print("📥 Bulk Content Importer for Facebook Posts")
    print("=" * 50)
    print("💡 Supports:")
    print("   • ChatGPT-generated tables")
    print("   • Numbered lists with captions/prompts")
    print("   • Simple text lists")
    print("   • Pipe-separated format")
    
    print("\n📝 Paste your content below (press Enter twice to finish):")
    print("-" * 30)
    
    # Get multi-line input
    lines = []
    while True:
        try:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        except EOFError:
            break
    
    content = '\n'.join(lines).strip()
    
    if not content:
        print("❌ No content provided.")
        return
    
    print(f"\n🔍 Parsing content ({len(content)} characters)...")
    
    # Parse the content
    posts = parse_chatgpt_content(content)
    
    if not posts:
        print("❌ No posts found in the content.")
        print("💡 Try formatting your content as:")
        print("   • Table: Title | Caption | Prompt | Type")
        print("   • List: 1. Post content")
        print("   • Simple: One post per line")
        return
    
    print(f"\n📱 Found {len(posts)} posts:")
    print("-" * 30)
    
    # Display preview
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. [{post['content_type']}] {post.get('title', 'Untitled')[:50]}...")
        if post.get('caption'):
            print(f"   Caption: {post['caption'][:50]}...")
        if post.get('prompt'):
            print(f"   Prompt: {post['prompt'][:50]}...")
    
    # Ask for confirmation
    confirm = input(f"\n✅ Add these {len(posts)} posts to Notion? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Operation cancelled.")
        return
    
    # Check if Notion token is available
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN environment variable not set!")
        print("💡 Set it with: export NOTION_TOKEN='your_token_here'")
        return
    
    # Add posts to Notion
    print(f"\n📤 Adding posts to Notion database...")
    success_count = 0
    
    for i, post in enumerate(posts, 1):
        print(f"   Adding post {i}/{len(posts)}...", end=" ")
        
        if add_post_to_notion(post):
            print("✅")
            success_count += 1
        else:
            print("❌")
    
    print(f"\n🎉 Successfully added {success_count}/{len(posts)} posts to Notion!")
    print("🔄 Picture posts will be processed by the image generator when Status='Waiting'")
    print("📱 Text posts are ready to be posted when Status='Pending'")

def show_format_examples():
    """Show examples of supported formats"""
    print("\n📋 Supported Content Formats:")
    print("=" * 40)
    
    print("\n1. TABLE FORMAT (pipe-separated):")
    print("Title | Caption | Prompt | Type")
    print("Marriage choice | You can only choose one: Love or Money? | Split screen image showing love symbols vs money symbols | Picture")
    print("Food question | What's your favorite Nigerian dish? | | Text")
    
    print("\n2. NUMBERED LIST FORMAT:")
    print("1. You can only choose one: Jollof rice or Fried rice?")
    print("Caption: Choose your side!")
    print("Prompt: Split screen image showing jollof rice vs fried rice")
    print("Type: Picture")
    print("")
    print("2. What's your favorite football team?")
    print("Type: Text")
    
    print("\n3. SIMPLE TEXT FORMAT:")
    print("Your wife earns double your salary. Are you still the head?")
    print("A cheating man who provides vs a faithful man who's broke")
    print("One has to go forever: rice or meat?")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        show_format_examples()
    else:
        main() 