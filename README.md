# Facebook Post Automation

This repository contains a GitHub Actions workflow that automatically moves posts from a Notion "Bank" database to a "Queue" database every hour. The Queue database is monitored by Zapier, which posts the content to your Facebook page.

## How It Works

1. **Notion Bank Database**: Contains all your prepared posts
2. **GitHub Actions**: Runs every hour, picks one post from Bank
3. **Notion Queue Database**: Has a single row that GitHub Actions adds comments to
4. **Zapier**: Monitors comments on the Queue row and posts to Facebook instantly

## Setup Instructions

### 1. GitHub Secrets Configuration

Go to your repository Settings > Secrets and variables > Actions, and add these secrets:

- `NOTION_TOKEN`: Your Notion integration token
- `NOTION_BANK_DB_ID`: Your Bank database ID
- `NOTION_QUEUE_DB_ID`: Your Queue database ID

### 2. Your Current Configuration

- **Notion Token**: `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`
- **Bank Database ID**: `225bc30eae8c80f48b48e67bcf5848ae`
- **Queue Database ID**: `225bc30eae8c8063b4b7ed9a424c1dec`

### 3. Database Structure

**Bank Database** should have:
- A title or text property containing your post content

**Queue Database** should have:
- A single row (any title/content)
- Zapier monitors comments on this row for new posts

### 4. Running the Workflow

The workflow runs automatically every hour. You can also trigger it manually:
1. Go to Actions tab in your repository
2. Click on "Move Notion Post to Queue"
3. Click "Run workflow"

## Files

- `move_post_notion.py`: Python script that handles the Notion API operations
- `.github/workflows/move_post_notion.yml`: GitHub Actions workflow configuration

## Troubleshooting

- Check the Actions tab for any error logs
- Ensure your Notion integration has access to both databases
- Verify that your database IDs are correct (32-character strings without dashes) 