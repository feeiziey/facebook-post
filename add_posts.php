<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$input = json_decode(file_get_contents('php://input'), true);

if (!$input || !isset($input['token']) || !isset($input['databaseId']) || !isset($input['posts'])) {
    http_response_code(400);
    echo json_encode(['error' => 'Missing required fields']);
    exit;
}

$token = $input['token'];
$databaseId = $input['databaseId'];
$posts = $input['posts'];

if (!is_array($posts)) {
    http_response_code(400);
    echo json_encode(['error' => 'Posts must be an array']);
    exit;
}

$results = [];
$successCount = 0;
$errorCount = 0;

// First, get database schema to find the correct property names
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, "https://api.notion.com/v1/databases/$databaseId");
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Authorization: Bearer ' . $token,
    'Content-Type: application/json',
    'Notion-Version: 2022-06-28'
]);

$response = curl_exec($ch);
$httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($httpCode !== 200) {
    http_response_code(500);
    echo json_encode(['error' => 'Failed to retrieve database schema']);
    exit;
}

$database = json_decode($response, true);
$properties = $database['properties'];

// Find the title property and status property
$titleProperty = null;
$statusProperty = null;

foreach ($properties as $propName => $propConfig) {
    if ($propConfig['type'] === 'title') {
        $titleProperty = $propName;
    }
    if ($propConfig['type'] === 'status') {
        $statusProperty = $propName;
    }
}

if (!$titleProperty) {
    http_response_code(500);
    echo json_encode(['error' => 'No title property found in database']);
    exit;
}

// Add each post
foreach ($posts as $index => $post) {
    $post = trim($post);
    if (empty($post)) continue;
    
    $pageProperties = [
        $titleProperty => [
            'title' => [
                [
                    'text' => [
                        'content' => $post
                    ]
                ]
            ]
        ]
    ];
    
    // Add status if it exists
    if ($statusProperty) {
        $pageProperties[$statusProperty] = [
            'status' => [
                'name' => 'Pending'
            ]
        ];
    }
    
    $data = [
        'parent' => [
            'database_id' => $databaseId
        ],
        'properties' => $pageProperties
    ];
    
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, 'https://api.notion.com/v1/pages');
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Authorization: Bearer ' . $token,
        'Content-Type: application/json',
        'Notion-Version: 2022-06-28'
    ]);
    
    $response = curl_exec($ch);
    $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
    curl_close($ch);
    
    if ($httpCode === 200) {
        $results[] = ['success' => true, 'post' => substr($post, 0, 50) . '...'];
        $successCount++;
    } else {
        $results[] = ['success' => false, 'post' => substr($post, 0, 50) . '...', 'error' => $response];
        $errorCount++;
    }
    
    // Small delay to avoid rate limiting
    usleep(100000); // 0.1 seconds
}

echo json_encode([
    'success' => true,
    'message' => "Added $successCount posts successfully, $errorCount failed",
    'results' => $results,
    'successCount' => $successCount,
    'errorCount' => $errorCount
]);
?> 