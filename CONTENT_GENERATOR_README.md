# 🎯 Facebook Content Generator & Bulk Importer

This toolkit provides two powerful tools for generating and importing Facebook posts for Nigerian audiences, specifically designed for engagement-focused "this or that" style content.

## 📋 What You Get

### 🤖 Automated Content Generator (`facebook_content_generator.py`)
- Generates 12 Facebook posts (6 picture posts + 6 text posts)
- Nigerian-specific content for topics like marriage, lifestyle, food, football
- Automatic "this or that" style captions for engagement
- AI-generated image prompts for picture posts
- Built-in content filtering (avoids inappropriate content)
- Direct integration with your Notion database

### 📥 Bulk Content Importer (`bulk_content_importer.py`)
- Import content from ChatGPT or other AI tools
- Supports multiple formats (tables, lists, simple text)
- Automatic parsing and column mapping
- Handles both picture and text posts
- Preview before importing to Notion

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Set your Notion token
export NOTION_TOKEN="your_notion_token_here"

# Make scripts executable
chmod +x facebook_content_generator.py
chmod +x bulk_content_importer.py
```

### 2. Generate Content Automatically
```bash
python3 facebook_content_generator.py
```

**Example interaction:**
```
Topics (comma-separated): marriage, lifestyle, food, football
Target audience/context: northern nigeria, nigerians, hausa  
Negative filters (comma-separated): sex, vulgar, explicit
```

**Generated content examples:**
- **Picture Post**: "You can only choose one: Jollof rice or Fried rice?"
- **Text Post**: "What's your favorite Nigerian dish? (All Nigerians welcome to share!)"

### 3. Import ChatGPT Content
```bash
python3 bulk_content_importer.py
```

**Supported formats:**

**Table Format:**
```
Title | Caption | Prompt | Type
Marriage choice | You can only choose one: Love or Money? | Split screen image showing love vs money symbols | Picture
Food question | What's your favorite Nigerian dish? | | Text
```

**Numbered List Format:**
```
1. You can only choose one: Jollof rice or Fried rice?
Caption: Choose your side!
Prompt: Split screen image showing jollof rice vs fried rice
Type: Picture

2. What's your favorite football team?
Type: Text
```

**Simple Text Format:**
```
Your wife earns double your salary. Are you still the head?
A cheating man who provides vs a faithful man who's broke
One has to go forever: rice or meat?
```

## 🎨 How It Works with Your Existing System

### Current Workflow:
1. **Content Generation** → Posts added to Notion with proper Status
2. **Image Generation** → FLUX.1-schnell processes "Waiting" picture posts
3. **Facebook Posting** → Zapier posts "Pending" content to Facebook

### Database Integration:
- **Picture Posts**: Status="Waiting", Content="Picture", Prompt filled
- **Text Posts**: Status="Pending", Content="Text", ready for posting
- **Generated Images**: Status changes to "Pending" after image creation

## 📊 Content Categories

### 🏠 Marriage & Relationships
- Traditional vs modern approaches
- Cultural perspectives
- Relationship dynamics
- Wedding traditions

### 🌆 Lifestyle
- Urban vs rural living
- Nigerian cultural choices
- Entertainment preferences
- Daily life decisions

### 🍲 Food & Cuisine
- Nigerian dishes comparisons
- Cooking methods
- Regional preferences
- Food culture

### ⚽ Football & Sports
- Team loyalties
- Player preferences
- League comparisons
- Sports culture

## 🎯 Nigerian-Specific Features

### Cultural Context
- Northern Nigeria perspectives
- Hausa community engagement
- Regional preferences
- Traditional vs modern values

### Engagement Optimization
- "This or that" format for maximum comments
- Culturally relevant choices
- Controversy-free content
- Community-building questions

## 🔧 Advanced Usage

### View Format Examples
```bash
python3 bulk_content_importer.py --examples
```

### Customize Content Templates
Edit the templates in `facebook_content_generator.py`:
- `THIS_OR_THAT_TEMPLATES`: Caption formats
- `TEXT_POST_TEMPLATES`: Question formats
- `content_ideas`: Topic-specific options

### Batch Processing
```bash
# Generate multiple batches
for i in {1..5}; do
    echo "marriage, lifestyle" | python3 facebook_content_generator.py
done
```

## 📈 Content Strategy Tips

### High-Engagement Topics
1. **Marriage & Relationships**: Always generates discussion
2. **Food Choices**: Nigerians are passionate about cuisine
3. **Football**: Universal engagement topic
4. **Lifestyle**: Regional differences create debate

### Optimal Posting Schedule
- **Picture Posts**: Take time to generate, schedule accordingly
- **Text Posts**: Ready immediately, can be posted frequently
- **Mix Ratio**: 50/50 picture/text for balanced engagement

### Audience Targeting
- **Northern Nigeria**: Focus on cultural values, traditional choices
- **General Nigerian**: Broader topics, national interests
- **Hausa Community**: Language-specific references, cultural nuances

## 🛠️ Troubleshooting

### Common Issues

**"No posts found"**
- Check content format
- Ensure proper delimiters (| for tables)
- Use numbered lists for structured content

**"Notion token error"**
```bash
export NOTION_TOKEN="ntn_your_token_here"
```

**"Database not found"**
- Verify database ID in script
- Check Notion integration permissions

### Content Quality Issues
- Adjust negative filters for stricter content control
- Modify templates for different engagement styles
- Update cultural references for target audience

## 🔄 Integration with Existing Workflows

### GitHub Actions
Your existing workflows will automatically:
1. Generate images for "Waiting" picture posts
2. Update status to "Pending" after image creation
3. Continue normal posting schedule

### Zapier Integration
- Text posts (Status="Pending") post immediately
- Picture posts post after image generation
- Maintains your current posting frequency

## 📞 Support & Customization

### Extending Topics
Add new categories to `content_ideas` dictionary:
```python
'new_topic': {
    'this_or_that': [
        ('Option A', 'Option B'),
        # more options...
    ],
    'text_posts': [
        'subtopic 1',
        'subtopic 2',
        # more subtopics...
    ]
}
```

### Custom Templates
Modify templates for different engagement styles:
- Questions vs statements
- Formal vs casual tone
- Regional vs national focus

---

🎉 **Ready to create engaging Facebook content for your Nigerian audience!**

The system is designed to work seamlessly with your existing FLUX.1-schnell image generation and Zapier posting workflows, providing a complete content automation solution. 