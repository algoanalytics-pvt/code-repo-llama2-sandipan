import mongoose from "mongoose";
import moment from "moment";
const alert = new mongoose.Schema(
  {
    Alert_Name: {
      type: String,
      required: [true, "alert name is required"],
      unique: [true, "alert name must be unique"],
    },
    No_Object_Status: {
      type: Boolean,
      required: [true, "no object status is required"],
    },
    Object_Class: {
      type: String,
      required: [true, "object class is required"],
    },
    Object_Area: [[{ type: Number }]],
    Start_Time: {
      type: String,
      required: [true, "start time is required"],
    },
    End_Time: {
      type: String,
      required: [true, "start time is required"],
    },
    Days_Active: [
      { type: String, required: [true, "Days Active is required"] },
    ],
    Holiday_Status: {
      type: Boolean,
      required: [true, "holiday status is required"],
    },
    Workday_Status: {
      type: Boolean,
      required: [true, "workday status is required"],
    },
    Alert_Status: {
      type: String,
      required: [true, "alert status is required"],
    },
    Display_Activation: {
      type: Boolean,
      required: [true, "display activation is required"],
    },
    Email_Activation: {
      type: Boolean,
      required: [true, "email activation is required"],
    },
    Timestamp: String,
    Camera_Name: [
      { type: String, required: [true, "camera name is required"] },
    ],
    Alert_Description: String,
  },
  {
    collection: "Alerts",
  }
);

alert.pre("save", async function (next) {
  this.Timestamp = moment.utc().format();
  next();
});

export default mongoose.model("Alerts", alert);
