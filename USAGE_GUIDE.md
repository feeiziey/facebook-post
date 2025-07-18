# 🚀 Quick Usage Guide

## 📋 What You Have Now

You now have **two powerful tools** for your Facebook post automation:

### 1. 🤖 **Automatic Content Generator** (`facebook_content_generator.py`)
- Generates 12 posts automatically
- Nigerian-focused content
- Perfect "this or that" engagement posts
- No external AI needed

### 2. 📥 **Bulk Content Importer** (`bulk_content_importer.py`)
- Import from ChatGPT
- Supports tables, lists, simple text
- Handles any format you throw at it

## 🎯 How to Use

### Option 1: Generate Content Automatically

```bash
# Set your Notion token (one time setup)
export NOTION_TOKEN="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"

# Run the generator
python3 facebook_content_generator.py
```

**What it asks:**
- Topics: `marriage, lifestyle, food, football` (or your own)
- Target audience: `northern nigeria, nigerians, hausa`
- Negative filters: `sex, vulgar, explicit`

**What you get:**
- 6 picture posts (Status="Waiting" for image generation)
- 6 text posts (Status="Pending" ready to post)
- All culturally relevant and engaging

### Option 2: Import from ChatGPT

```bash
# Run the importer
python3 bulk_content_importer.py
```

**Then paste your ChatGPT content in any format:**

**Table format:**
```
Title | Caption | Prompt | Type
Marriage choice | You can only choose one: Love or Money? | Split screen love vs money | Picture
Food question | What's your favorite Nigerian dish? | | Text
```

**Simple list:**
```
Your wife earns double your salary. Are you still the head?
A cheating man who provides vs a faithful man who's broke
One has to go forever: rice or meat?
```

## 🔄 How It Works with Your System

### Current Flow:
1. **Generate Content** → Added to Notion
2. **FLUX.1-schnell** → Processes "Waiting" picture posts
3. **Zapier** → Posts "Pending" content to Facebook

### Perfect Integration:
- Picture posts get images generated automatically
- Text posts are ready to post immediately
- Your existing workflows continue unchanged

## 🎨 Sample Generated Content

### Picture Posts (with prompts):
- "You can only choose one: Jollof rice or Fried rice?"
- "Team Manchester United or Team Manchester City?"
- "One has to go forever: Lagos life or Abuja life?"

### Text Posts (ready to post):
- "What's your favorite Nigerian dish? (Northern Nigeria perspective welcome!)"
- "Which football team do you support and why?"
- "Share your best marriage advice in the comments!"

## 🛠️ Quick Setup

1. **Set your Notion token:**
   ```bash
   export NOTION_TOKEN="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"
   ```

2. **Test the generator:**
   ```bash
   python3 demo_content_generator.py
   ```

3. **Generate real content:**
   ```bash
   python3 facebook_content_generator.py
   ```

## 💡 Pro Tips

### For Maximum Engagement:
- Use controversial but safe topics (food choices, team preferences)
- Mix picture and text posts 50/50
- Target specific Nigerian cultural contexts
- Ask questions that require choosing sides

### Content Strategy:
- **Marriage topics**: Always generate massive engagement
- **Food choices**: Nigerians are passionate about cuisine
- **Football**: Universal engagement topic
- **Lifestyle**: Regional differences create healthy debate

### Automation:
- Picture posts take time to generate images
- Text posts can be scheduled immediately
- Your existing 30-minute workflow continues perfectly

## 🎉 You're Ready!

Your Facebook engagement automation is now complete:
- ✅ Content generation (manual or automatic)
- ✅ High-quality image generation (FLUX.1-schnell)
- ✅ Automatic posting (Zapier)
- ✅ Nigerian cultural context
- ✅ Engagement-optimized formats

Just run the tools whenever you need fresh content! 