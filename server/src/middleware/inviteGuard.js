/**
 * Davet kodu korumasi ve IP bazli gecici engel mekanizmasi.
 * 5 yanlis denemede IP 15 dakika bloke edilir.
 */
const INVITE_CODE = 'İAZEMY68';
const MAX_FAILED_ATTEMPTS = 5;
const BLOCK_DURATION_MS = 15 * 60 * 1000;

// Basit in-memory takip (tek sunucu instance icin yeterli)
const ipAttempts = new Map();

function inviteGuard(req, res, next) {
  const ip = req.ip;
  const entry = ipAttempts.get(ip);

  if (entry?.blockedUntil && Date.now() < entry.blockedUntil) {
    const waitSeconds = Math.ceil((entry.blockedUntil - Date.now()) / 1000);
    return res.status(429).json({
      message: `Bu IP gecici olarak engellendi. ${waitSeconds} saniye sonra tekrar deneyin.`
    });
  }

  const { inviteCode } = req.body;
  if (inviteCode === INVITE_CODE) {
    ipAttempts.delete(ip);
    return next();
  }

  const failedCount = (entry?.failedCount || 0) + 1;
  const newEntry = { failedCount };

  if (failedCount >= MAX_FAILED_ATTEMPTS) {
    newEntry.blockedUntil = Date.now() + BLOCK_DURATION_MS;
    newEntry.failedCount = 0;
  }

  ipAttempts.set(ip, newEntry);

  return res.status(403).json({
    message:
      failedCount >= MAX_FAILED_ATTEMPTS
        ? 'Cok fazla hatali kod girdiniz. IP gecici olarak engellendi.'
        : 'Davet kodu gecersiz.'
  });
}

module.exports = { inviteGuard };
