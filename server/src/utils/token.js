const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'CHANGE_ME_FOR_PRODUCTION';

function signToken(user) {
  return jwt.sign(
    {
      userId: user._id,
      username: user.username
    },
    JWT_SECRET,
    { expiresIn: '7d' }
  );
}

module.exports = { signToken };
