<?php

declare(strict_types=1);

require_once __DIR__ . '/../config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['ok' => false, 'message' => 'Method not allowed'], 405);
}

$body = get_json_body();
$email = strtolower(trim((string)($body['email'] ?? '')));

if ($email !== ADMIN_EMAIL) {
    json_response(['ok' => false, 'message' => 'Bu e-posta yetkili değil'], 403);
}

$code = (string) random_int(100000, 999999);
$_SESSION['otp_code'] = $code;
$_SESSION['otp_email'] = $email;
$_SESSION['otp_expires'] = time() + 600;

// Demo: Gerçek sistemde burada SMTP/API ile e-posta gönderilir.
json_response([
    'ok' => true,
    'message' => 'Kod üretildi (demo)',
    'demoCode' => $code,
]);
