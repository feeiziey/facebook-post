const express = require('express');
const cors = require('cors');
const { Client } = require('@notionhq/client');

const app = express();
const port = process.env.PORT || 3000;

// Enable CORS for all routes
app.use(cors());
app.use(express.json());

// Serve static files (your HTML page)
app.use(express.static('.'));

// Endpoint to add posts to Notion
app.post('/api/add-posts', async (req, res) => {
    try {
        const { token, databaseId, posts } = req.body;
        
        if (!token || !databaseId || !posts || !Array.isArray(posts)) {
            return res.status(400).json({ error: 'Missing required fields' });
        }

        const notion = new Client({ auth: token });
        
        const results = [];
        
        for (let i = 0; i < posts.length; i++) {
            const post = posts[i].trim();
            
            if (!post) continue;
            
            try {
                const response = await notion.pages.create({
                    parent: {
                        database_id: databaseId
                    },
                    properties: {
                        'Post': {
                            title: [
                                {
                                    text: {
                                        content: post
                                    }
                                }
                            ]
                        },
                        'Status': {
                            status: {
                                name: 'Pending'
                            }
                        }
                    }
                });
                
                results.push({ success: true, post: post.substring(0, 50) + '...' });
                
                // Small delay to avoid rate limiting
                await new Promise(resolve => setTimeout(resolve, 100));
                
            } catch (error) {
                console.error(`Error adding post ${i + 1}:`, error);
                results.push({ success: false, post: post.substring(0, 50) + '...', error: error.message });
            }
        }
        
        const successCount = results.filter(r => r.success).length;
        const errorCount = results.filter(r => !r.success).length;
        
        res.json({
            success: true,
            message: `Added ${successCount} posts successfully, ${errorCount} failed`,
            results: results,
            successCount,
            errorCount
        });
        
    } catch (error) {
        console.error('Server error:', error);
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
}); 