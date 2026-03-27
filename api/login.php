<?php

declare(strict_types=1);

require_once __DIR__ . '/../config.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    json_response(['ok' => false, 'message' => 'Method not allowed'], 405);
}

$body = get_json_body();
$email = strtolower(trim((string)($body['email'] ?? '')));
$code = trim((string)($body['code'] ?? ''));

if ($email !== ADMIN_EMAIL) {
    json_response(['ok' => false, 'message' => 'Yetkili e-posta gerekli'], 403);
}

if (!isset($_SESSION['otp_code'], $_SESSION['otp_email'], $_SESSION['otp_expires'])) {
    json_response(['ok' => false, 'message' => 'Önce kod gönderin'], 400);
}

if (time() > (int) $_SESSION['otp_expires']) {
    json_response(['ok' => false, 'message' => 'Kodun süresi dolmuş'], 400);
}

if ($_SESSION['otp_email'] !== $email || $_SESSION['otp_code'] !== $code) {
    json_response(['ok' => false, 'message' => 'Kod hatalı'], 400);
}

$_SESSION['is_admin'] = true;
unset($_SESSION['otp_code'], $_SESSION['otp_email'], $_SESSION['otp_expires']);

json_response(['ok' => true, 'message' => 'Giriş başarılı']);
