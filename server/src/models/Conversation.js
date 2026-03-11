const mongoose = require('mongoose');

const conversationSchema = new mongoose.Schema(
  {
    name: {
      type: String,
      required: true,
      unique: true,
      trim: true,
      maxlength: 60
    }
  },
  { timestamps: true }
);

module.exports = mongoose.model('Conversation', conversationSchema);
