<?php

declare(strict_types=1);

require_once __DIR__ . '/../config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['ok' => false, 'message' => 'Method not allowed'], 405);
}

$_SESSION = [];
if (session_id() !== '') {
    session_destroy();
}

json_response(['ok' => true, 'message' => 'Çıkış yapıldı']);
