#!/usr/bin/env python3
"""
Demo script for Facebook Content Generator
Shows generated content without requiring Notion token
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from facebook_content_generator import generate_content_with_ai

def demo_content_generation():
    """Demonstrate content generation with sample inputs"""
    print("🎯 Facebook Content Generator Demo")
    print("=" * 50)
    
    # Sample inputs
    topics = "marriage, lifestyle, food, football"
    target_audience = "northern nigeria, nigerians, hausa"
    negative_filters = "sex, vulgar, explicit"
    
    print(f"📋 Topics: {topics}")
    print(f"🎯 Audience: {target_audience}")
    print(f"🚫 Avoiding: {negative_filters}")
    
    print(f"\n🤖 Generating 12 Facebook posts...")
    
    # Generate content
    posts = generate_content_with_ai(topics, target_audience, negative_filters)
    
    print(f"\n📱 Generated {len(posts)} posts:")
    print("=" * 50)
    
    # Display all posts with full details
    picture_posts = [p for p in posts if p['type'] == 'picture']
    text_posts = [p for p in posts if p['type'] == 'text']
    
    print(f"\n🖼️  PICTURE POSTS ({len(picture_posts)}):")
    print("-" * 30)
    for i, post in enumerate(picture_posts, 1):
        print(f"\n{i}. Topic: {post['topic'].title()}")
        print(f"   Caption: {post['caption']}")
        print(f"   Prompt: {post['prompt']}")
        print(f"   Status: Waiting (for image generation)")
        print(f"   Content: Picture")
    
    print(f"\n📝 TEXT POSTS ({len(text_posts)}):")
    print("-" * 30)
    for i, post in enumerate(text_posts, 1):
        print(f"\n{i}. Topic: {post['topic'].title()}")
        print(f"   Content: {post['content']}")
        print(f"   Status: Pending (ready to post)")
        print(f"   Content: Text")
    
    print(f"\n🔄 Integration with Your System:")
    print("=" * 40)
    print("✅ Picture posts will be processed by FLUX.1-schnell")
    print("✅ Text posts are ready for immediate posting")
    print("✅ All posts follow Nigerian cultural context")
    print("✅ Content filtered for appropriateness")
    
    return posts

if __name__ == "__main__":
    posts = demo_content_generation()
    
    print(f"\n🎉 Demo Complete!")
    print(f"Generated {len(posts)} engaging Facebook posts")
    print("Ready to integrate with your Notion database!") 