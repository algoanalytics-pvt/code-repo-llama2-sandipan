import mongoose from "mongoose";
const debug = require("debug")("author");

const DATABASE = process.env.DATABASE;

mongoose
  .connect(DATABASE)
  .then(() => {
    debug("connection successful");
  })
  .catch(() => {
    debug("connection failed");
  });
