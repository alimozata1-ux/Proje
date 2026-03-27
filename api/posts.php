<?php

declare(strict_types=1);

require_once __DIR__ . '/../config.php';

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

if ($method === 'GET') {
    $posts = read_posts();
    json_response([
        'ok' => true,
        'posts' => $posts,
        'isAdmin' => (($_SESSION['is_admin'] ?? false) === true),
    ]);
}

if ($method === 'POST') {
    require_admin();

    $body = get_json_body();
    $tab = (string) ($body['tab'] ?? '');

    $allowedTabs = ['schematics', 'codes', 'apps', 'announcements'];
    if (!in_array($tab, $allowedTabs, true)) {
        json_response(['ok' => false, 'message' => 'Geçersiz sekme'], 422);
    }

    $title = trim((string) ($body['title'] ?? ''));
    $content = trim((string) ($body['content'] ?? ''));

    if ($title === '' || $content === '') {
        json_response(['ok' => false, 'message' => 'Başlık ve içerik zorunlu'], 422);
    }

    $post = [
        'id' => uniqid('pst_', true),
        'title' => $title,
        'summary' => trim((string) ($body['summary'] ?? '')),
        'content' => $content,
        'code' => (string) ($body['code'] ?? ''),
        'image' => trim((string) ($body['image'] ?? '')),
        'tags' => is_array($body['tags'] ?? null) ? array_values($body['tags']) : [],
        'pinned' => (bool) ($body['pinned'] ?? false),
        'type' => in_array(($body['type'] ?? 'normal'), ['normal', 'scheduled'], true) ? $body['type'] : 'normal',
        'scheduledAt' => (string) ($body['scheduledAt'] ?? ''),
        'createdAt' => date('Y-m-d H:i:s'),
    ];

    $posts = read_posts();
    if (!isset($posts[$tab]) || !is_array($posts[$tab])) {
        $posts[$tab] = [];
    }
    $posts[$tab][] = $post;
    write_posts($posts);

    json_response(['ok' => true, 'message' => 'Paylaşım eklendi', 'post' => $post]);
}

json_response(['ok' => false, 'message' => 'Method not allowed'], 405);
