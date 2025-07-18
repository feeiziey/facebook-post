#!/usr/bin/env python3
"""
Facebook Content Generator for Nigerian Audience
Generates engaging "this or that" picture posts and text posts based on topics
"""

import os
import requests
import json
import random
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

# Content templates for "this or that" posts
THIS_OR_THAT_TEMPLATES = [
    "You can only choose one: {option1} or {option2}?",
    "Pick one and explain why: {option1} vs {option2}",
    "One has to go forever: {option1} or {option2}?",
    "If you had to choose: {option1} or {option2}?",
    "Which would you rather: {option1} or {option2}?",
    "Choose your side: {option1} or {option2}?",
    "One must stay, one must go: {option1} vs {option2}",
    "Team {option1} or Team {option2}? Choose wisely!",
]

# Text post templates
TEXT_POST_TEMPLATES = [
    "What's your take on {topic}? Share your thoughts!",
    "Which {topic} do you prefer and why?",
    "What's the best {topic} you've ever experienced?",
    "If you could change one thing about {topic}, what would it be?",
    "What's your unpopular opinion about {topic}?",
    "Share your favorite {topic} memory in the comments!",
    "What's the most important thing about {topic} to you?",
    "Which {topic} trend do you think will last?",
]

def generate_content_with_ai(topics, target_audience, negative_filters):
    """
    Generate Facebook post content using AI-style logic
    This simulates what ChatGPT would generate for Nigerian audience
    """
    
    # Split topics into individual items
    topic_list = [t.strip() for t in topics.split(',')]
    
    # Nigerian-specific content ideas based on your topics
    content_ideas = {
        'marriage': {
            'this_or_that': [
                ('A man who cooks', 'A man who provides everything'),
                ('Love marriage', 'Arranged marriage'),
                ('Big wedding', 'Court wedding + honeymoon'),
                ('Stay-at-home wife', 'Working wife'),
                ('Husband who travels', 'Husband who stays home'),
                ('Traditional wedding', 'White wedding'),
                ('Polygamy', 'Monogamy'),
                ('Early marriage', 'Late marriage'),
            ],
            'text_posts': [
                'marriage in Nigeria',
                'wedding traditions',
                'spouse qualities',
                'marriage advice',
                'relationship goals',
                'wedding planning',
                'marriage counseling',
                'family values'
            ]
        },
        'lifestyle': {
            'this_or_that': [
                ('Lagos life', 'Abuja life'),
                ('Village life', 'City life'),
                ('Generator', 'Solar power'),
                ('Okada', 'Keke napep'),
                ('Suya', 'Kilishi'),
                ('Nollywood', 'Hollywood'),
                ('Jollof rice', 'Fried rice'),
                ('Weekend in Lagos', 'Weekend in Dubai'),
            ],
            'text_posts': [
                'Nigerian lifestyle',
                'city living',
                'weekend activities',
                'Nigerian culture',
                'modern vs traditional',
                'urban vs rural',
                'entertainment choices',
                'lifestyle changes'
            ]
        },
        'food': {
            'this_or_that': [
                ('Jollof rice', 'Fried rice'),
                ('Amala', 'Pounded yam'),
                ('Suya', 'Pepper soup'),
                ('Indomie', 'Spaghetti'),
                ('Boli', 'Roasted corn'),
                ('Garri', 'Rice'),
                ('Meat pie', 'Sausage roll'),
                ('Zobo', 'Chapman'),
            ],
            'text_posts': [
                'Nigerian cuisine',
                'favorite dishes',
                'cooking methods',
                'food combinations',
                'street food',
                'home cooking',
                'restaurant vs home food',
                'food memories'
            ]
        },
        'football': {
            'this_or_that': [
                ('Manchester United', 'Manchester City'),
                ('Real Madrid', 'Barcelona'),
                ('Premier League', 'La Liga'),
                ('Messi', 'Ronaldo'),
                ('Arsenal', 'Chelsea'),
                ('Liverpool', 'Tottenham'),
                ('Champions League', 'World Cup'),
                ('Playing football', 'Watching football'),
            ],
            'text_posts': [
                'football in Nigeria',
                'favorite teams',
                'football legends',
                'local vs international football',
                'football memories',
                'Super Eagles',
                'football predictions',
                'football culture'
            ]
        }
    }
    
    # Generate 12 posts (6 picture posts, 6 text posts)
    posts = []
    
    # Generate 6 picture posts (this or that style)
    for i in range(6):
        topic = random.choice(topic_list).lower()
        
        # Find matching content or create generic
        if topic in content_ideas:
            options = random.choice(content_ideas[topic]['this_or_that'])
        else:
            # Generic options for any topic
            options = (f"Traditional {topic}", f"Modern {topic}")
        
        # Create caption
        caption_template = random.choice(THIS_OR_THAT_TEMPLATES)
        caption = caption_template.format(option1=options[0], option2=options[1])
        
        # Create image prompt
        prompt = f"Split screen image showing {options[0]} on the left side and {options[1]} on the right side, with 'VS' in the middle, colorful and engaging design, Nigerian context, high quality digital art"
        
        # Filter out negative content
        if not any(neg.lower() in caption.lower() or neg.lower() in prompt.lower() for neg in negative_filters.split(',')):
            posts.append({
                'type': 'picture',
                'caption': caption,
                'prompt': prompt,
                'topic': topic
            })
    
    # Generate 6 text posts
    for i in range(6):
        topic = random.choice(topic_list).lower()
        
        # Find matching content or create generic
        if topic in content_ideas:
            text_topic = random.choice(content_ideas[topic]['text_posts'])
        else:
            text_topic = topic
        
        # Create text post
        text_template = random.choice(TEXT_POST_TEMPLATES)
        text_content = text_template.format(topic=text_topic)
        
        # Add Nigerian context
        if target_audience and 'nigeria' in target_audience.lower():
            if 'northern' in target_audience.lower():
                text_content += " (Northern Nigeria perspective welcome!)"
            elif 'hausa' in target_audience.lower():
                text_content += " (Hausa community thoughts needed!)"
            else:
                text_content += " (All Nigerians welcome to share!)"
        
        # Filter out negative content
        if not any(neg.lower() in text_content.lower() for neg in negative_filters.split(',')):
            posts.append({
                'type': 'text',
                'content': text_content,
                'topic': topic
            })
    
    return posts

def add_post_to_notion(post_data):
    """Add a single post to Notion database"""
    
    if post_data['type'] == 'picture':
        # Picture post
        page_properties = {
            'Name': {  # Assuming title property is called 'Name'
                'title': [
                    {
                        'text': {
                            'content': post_data['caption']
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
                            'content': post_data['prompt']
                        }
                    }
                ]
            }
        }
    else:
        # Text post
        page_properties = {
            'Name': {  # Assuming title property is called 'Name'
                'title': [
                    {
                        'text': {
                            'content': post_data['content']
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
    """Main function to generate and populate content"""
    print("🎯 Facebook Content Generator for Nigerian Audience")
    print("=" * 50)
    
    # Get user inputs
    print("\n📝 Enter your content parameters:")
    topics = input("Topics (comma-separated): ").strip()
    if not topics:
        topics = "marriage, lifestyle, food, football"
        print(f"Using default topics: {topics}")
    
    target_audience = input("Target audience/context: ").strip()
    if not target_audience:
        target_audience = "northern nigeria, nigerians, hausa"
        print(f"Using default audience: {target_audience}")
    
    negative_filters = input("Negative filters (comma-separated): ").strip()
    if not negative_filters:
        negative_filters = "sex, vulgar, explicit"
        print(f"Using default filters: {negative_filters}")
    
    print(f"\n🤖 Generating 12 Facebook posts...")
    print(f"📋 Topics: {topics}")
    print(f"🎯 Audience: {target_audience}")
    print(f"🚫 Avoiding: {negative_filters}")
    
    # Generate content
    posts = generate_content_with_ai(topics, target_audience, negative_filters)
    
    print(f"\n📱 Generated {len(posts)} posts:")
    print("-" * 30)
    
    # Display preview
    for i, post in enumerate(posts, 1):
        print(f"\n{i}. [{post['type'].upper()}] {post['topic'].title()}")
        if post['type'] == 'picture':
            print(f"   Caption: {post['caption']}")
            print(f"   Prompt: {post['prompt'][:60]}...")
        else:
            print(f"   Content: {post['content']}")
    
    # Ask for confirmation
    confirm = input("\n✅ Add these posts to Notion? (y/n): ").strip().lower()
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

if __name__ == "__main__":
    main() 