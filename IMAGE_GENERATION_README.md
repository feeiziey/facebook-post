# Multi-Provider Image Generation System

## Overview
This system generates images for Facebook posts using multiple AI image generation services with automatic fallback when one service is unavailable or has exceeded limits.

## Current AI Models Used

### 1. FLUX.1-schnell (Primary)
- **Provider**: Hugging Face Inference API
- **Quality**: High-quality, fast generation
- **Cost**: Requires Hugging Face credits
- **Status**: Currently exceeded monthly limit

### 2. Free API Placeholder (Fallback)
- **Provider**: Local placeholder generation
- **Quality**: Basic placeholder with text
- **Cost**: Free
- **Status**: ✅ Working as fallback

## How It Works

### Automatic Fallback System
1. **First Attempt**: Tries Hugging Face FLUX.1-schnell
2. **If Failed**: Automatically falls back to Free API Placeholder
3. **File Naming**: Images are named based on the model used:
   - `flux_generated_YYYYMMDD_HHMMSS_N.png` (FLUX.1-schnell)
   - `freeapi_generated_YYYYMMDD_HHMMSS_N.png` (Free API Placeholder)

### Error Handling
- **402 Error**: Hugging Face credits exceeded → switches to Free API Placeholder
- **503 Error**: Model loading → waits and retries
- **Timeout**: Moves to next service

## Current Issue
You've exceeded your monthly Hugging Face credits. The system will now automatically use Free API Placeholder as the fallback.

## Solutions

### Option 1: Upgrade Hugging Face (Recommended)
1. Go to [Hugging Face Pro](https://huggingface.co/pro)
2. Subscribe to get 20x more monthly credits
3. Continue using high-quality FLUX.1-schnell

### Option 2: Use Free Alternative
The system now automatically uses Free API Placeholder when Hugging Face is unavailable.

### Option 3: Add More Free Services
We can add more free alternatives like:
- Replicate (free tier)
- RunPod (free tier)
- LocalAI (self-hosted)

## Testing
Run the test script to verify the system works:
```bash
python test_image_generation.py
```

## Configuration
Environment variables needed:
- `NOTION_TOKEN`: For accessing your Notion database
- `HUGGINGFACE_TOKEN`: For Hugging Face API (optional, will use fallback if not available)

## File Structure
```
generate_images.py          # Main image generation script
test_image_generation.py    # Test script
IMAGE_GENERATION_README.md  # This file
images/                     # Generated images directory
```

## Next Steps
1. **Immediate**: The system will now work with Free API Placeholder
2. **Short-term**: Consider upgrading Hugging Face for better quality
3. **Long-term**: Add more free alternatives for redundancy 