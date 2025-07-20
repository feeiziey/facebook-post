#!/usr/bin/env python3
"""
Test script for multi-provider image generation
"""

import os
import sys
from generate_images import generate_image_with_fallback

def test_image_generation():
    """Test the image generation with a simple prompt"""
    print("🧪 Testing Multi-Provider Image Generation")
    print("=" * 50)
    
    test_prompt = "A beautiful sunset over mountains, digital art style"
    
    print(f"📝 Test prompt: {test_prompt}")
    print()
    
    # Test the fallback system
    image_data, model_used = generate_image_with_fallback(test_prompt)
    
    if image_data:
        print(f"✅ Success! Generated image using: {model_used}")
        print(f"📊 Image size: {len(image_data)} bytes")
        
        # Save test image
        os.makedirs('images', exist_ok=True)
        test_filename = f'test_generated_{model_used.lower().replace(".", "_").replace(" ", "_")}.png'
        
        with open(f'images/{test_filename}', 'wb') as f:
            f.write(image_data)
        
        print(f"💾 Test image saved as: images/{test_filename}")
        return True
    else:
        print("❌ Failed to generate test image")
        return False

if __name__ == '__main__':
    success = test_image_generation()
    sys.exit(0 if success else 1) 