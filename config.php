<?php

declare(strict_types=1);

const ADMIN_EMAIL = 'alimozata1@gmail.com';
const DATA_FILE = __DIR__ . '/storage/posts.json';

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

function json_response(array $payload, int $status = 200): void
{
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($payload, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
    exit;
}

function read_posts(): array
{
    if (!file_exists(DATA_FILE)) {
        $seed = seed_posts();
        file_put_contents(DATA_FILE, json_encode($seed, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
        return $seed;
    }

    $raw = file_get_contents(DATA_FILE);
    if ($raw === false || trim($raw) === '') {
        return seed_posts();
    }

    $decoded = json_decode($raw, true);
    if (!is_array($decoded)) {
        return seed_posts();
    }

    return $decoded;
}

function write_posts(array $posts): void
{
    file_put_contents(DATA_FILE, json_encode($posts, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT));
}

function seed_posts(): array
{
    $now = date('Y-m-d H:i:s');

    return [
        'schematics' => [
            [
                'id' => uniqid('sch_', true),
                'title' => 'LED + Buton Devresi',
                'summary' => 'Başlangıç seviyesi bağlantı',
                'content' => 'Pin13 LED, Pin2 buton. 220R direnç kullan.',
                'code' => 'pinMode(13, OUTPUT); pinMode(2, INPUT_PULLUP);',
                'image' => '',
                'tags' => ['arduino', 'led', 'buton'],
                'pinned' => true,
                'type' => 'normal',
                'scheduledAt' => '',
                'createdAt' => $now,
            ],
        ],
        'codes' => [
            [
                'id' => uniqid('cod_', true),
                'title' => 'Blink Kodu',
                'summary' => 'LED yak/söndür',
                'content' => 'Temel blink örneği',
                'code' => "void setup(){pinMode(13,OUTPUT);} void loop(){digitalWrite(13,1);delay(500);digitalWrite(13,0);delay(500);}",
                'image' => '',
                'tags' => ['blink'],
                'pinned' => false,
                'type' => 'normal',
                'scheduledAt' => '',
                'createdAt' => $now,
            ],
        ],
        'apps' => [],
        'announcements' => [
            [
                'id' => uniqid('ann_', true),
                'title' => 'Yakında Yeni Set',
                'summary' => 'Sensör seti anlatımı gelecek',
                'content' => 'DS18B20 ve DHT11 içerikleri eklenecek.',
                'code' => '',
                'image' => '',
                'tags' => ['duyuru'],
                'pinned' => true,
                'type' => 'scheduled',
                'scheduledAt' => '',
                'createdAt' => $now,
            ],
        ],
    ];
}

function require_admin(): void
{
    if (($_SESSION['is_admin'] ?? false) !== true) {
        json_response(['ok' => false, 'message' => 'Yetkisiz erişim'], 401);
    }
}

function get_json_body(): array
{
    $raw = file_get_contents('php://input');
    if ($raw === false || trim($raw) === '') {
        return [];
    }

    $decoded = json_decode($raw, true);
    return is_array($decoded) ? $decoded : [];
}
