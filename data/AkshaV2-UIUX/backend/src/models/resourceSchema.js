import mongoose from "mongoose";

const notification = new mongoose.Schema(
  {
    notification_email: [{ type: String }],
    username: {
      type: String,
      required: [true, "Username is required"],
      unique: [true, "Username must be unique"],
    },
    new_email: {
      type: String,
      required: [true, "New_Email is required"],
      unique: [true, "New_Email must be unique"],
    },
  },
  {
    collection: "Resource",
  }
);

export default mongoose.model("Resource", notification);
