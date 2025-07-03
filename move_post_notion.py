import os
from notion_client import Client

# Initialize Notion client
notion = Client(auth=os.environ["NOTION_TOKEN"])
bank_db = os.environ["NOTION_BANK_DB_ID"]
queue_db = os.environ["NOTION_QUEUE_DB_ID"]

try:
    # Get the first unposted post from Bank
    print("Fetching posts from Bank database...")
    results = notion.databases.query(
        database_id=bank_db,
        page_size=1,
        sorts=[
            {
                "timestamp": "created_time",
                "direction": "ascending"
            }
        ]
    )
    
    if not results["results"]:
        print("No posts left in Bank database.")
        exit(0)

    post = results["results"][0]
    
    # Extract post content (assuming the first property is the content)
    post_properties = post["properties"]
    
    # Find the content property (usually the first text/title property)
    content_property = None
    content_text = ""
    
    for prop_name, prop_value in post_properties.items():
        if prop_value["type"] == "title" and prop_value["title"]:
            content_text = prop_value["title"][0]["plain_text"]
            content_property = prop_name
            break
        elif prop_value["type"] == "rich_text" and prop_value["rich_text"]:
            content_text = prop_value["rich_text"][0]["plain_text"]
            content_property = prop_name
            break
    
    if not content_text:
        print("No content found in the post.")
        exit(1)

    print(f"Found post: {content_text[:50]}...")

    # Add comment to the Queue database (single row)
    print("Adding comment to Queue database...")
    
    # First, get the single row in the Queue database
    queue_results = notion.databases.query(database_id=queue_db, page_size=1)
    
    if not queue_results["results"]:
        print("No row found in Queue database. Please create a single row first.")
        exit(1)
    
    queue_page_id = queue_results["results"][0]["id"]
    
    # Add comment to the Queue row
    notion.comments.create(
        parent={"page_id": queue_page_id},
        rich_text=[
            {
                "text": {
                    "content": content_text
                }
            }
        ]
    )

    # Delete from Bank database
    print("Removing post from Bank database...")
    notion.pages.update(
        page_id=post["id"],
        archived=True
    )

    print(f"Successfully moved post: {content_text[:100]}...")

except Exception as e:
    print(f"Error: {e}")
    exit(1) 