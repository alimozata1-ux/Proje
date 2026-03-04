const mongoose = require('mongoose');

async function connectDatabase() {
  const uri = process.env.MONGODB_URI;

  if (!uri) {
    throw new Error('MONGODB_URI tanimli degil. Lutfen .env dosyasina ekleyin.');
  }

  await mongoose.connect(uri);
  console.log('MongoDB baglantisi basarili');
}

module.exports = { connectDatabase };
