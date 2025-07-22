#!/usr/bin/env python3
"""
Test script for quote-style fallback image generation
"""

from generate_images import generate_image_with_free_api
import os

def test_quote_image():
    prompt = "Mastering others is strength. Mastering yourself is true power."
    print(f"🧪 Testing quote-style fallback image for prompt: {prompt}")
    image_data = generate_image_with_free_api(prompt)
    if image_data:
        os.makedirs('images', exist_ok=True)
        filename = 'test_quote_fallback.png'
        with open(f'images/{filename}', 'wb') as f:
            f.write(image_data)
        print(f"✅ Test image saved as images/{filename}")
    else:
        print("❌ Failed to generate quote-style fallback image")

if __name__ == '__main__':
    test_quote_image() 