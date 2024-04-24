import mongoose from "mongoose";

const cameraDetail = new mongoose.Schema(
  {
    Rtsp_Link: {
      type: String,
      required: [true, "Rtsp_Link is required"],
      unique: [true, "Rtsp_Link must be unique"],
    },
    Camera_Name: {
      type: String,
      required: [true, "camera name is required"],
      unique: [true, "camera name must be unique"],
    },
    Description: String,
    Feature: [{ type: String }],
    Priority: String,
    Status: String,
    Email_Auto_Alert: Boolean,
    Display_Auto_Alert: Boolean,
    Email_Alert: Boolean,
    Display_Alert: Boolean,
    Skip_Interval: Number,
    //Alert: [{ type: String }],
    Alerts: [{ type: mongoose.Schema.Types.ObjectId, ref: 'alert' }],
    Active: Boolean,
    Live: {
      type: Boolean,
      default: true,
    },
    Surveillance_Status: {
      type: String,
      default: "start",
    },
    PausedTime: {
      type: String,
      default: "null",
    },
  },
  { collection: "config" }
);

export default mongoose.model("config", cameraDetail);
