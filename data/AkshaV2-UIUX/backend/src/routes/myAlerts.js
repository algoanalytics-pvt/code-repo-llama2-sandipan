import express from "express";
import Alert from "../models/myAlertSchema";
import config from "../models/configSchema";
const router = express.Router();

router.post(process.env.CREATE_ALERT, async (req, res) => {
  const {
    Alert_Name,
    Object_Class,
    Object_Area,
    Start_Time,
    End_Time,
    Days_Active,
    Holiday_Status,
    Workday_Status,
    Alert_Status,
    Display_Activation,
    Email_Activation,
    Camera_Name,
    Alert_Description,
    No_Object_Status
  } = req.body;

  try {
    const newAlert = new Alert({
      Alert_Name: Alert_Name,
      Object_Class: Object_Class,
      Object_Area: Object_Area,
      Start_Time: Start_Time,
      End_Time: End_Time,
      Days_Active: Days_Active,
      Holiday_Status: Holiday_Status,
      Workday_Status: Workday_Status,
      Alert_Status: Alert_Status,
      Display_Activation: Display_Activation,
      Email_Activation: Email_Activation,
      Camera_Name: Camera_Name,
      Alert_Description: Alert_Description,
      No_Object_Status:No_Object_Status,
    });

    await newAlert.save();

    await config.updateMany(
      { Camera_Name: { $in: Camera_Name } },
      { $push: { Alerts: newAlert.id  } }
    );

    res.status(200).json({
      success: true,
      message: "alert creation successful",
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
    });
  }
});

router.put(process.env.UPDATE_ALERT, async (req, res) => {
  const {
    Alert_Name,
    Object_Class,
    Object_Area,
    Start_Time,
    End_Time,
    Days_Active,
    Holiday_Status,
    Workday_Status,
    Alert_Status,
    Display_Activation,
    Email_Activation,
    Camera_Name,
    Alert_Description,
    No_Object_Status
  } = req.body;

  try {
    await Alert.findByIdAndUpdate(
      { _id: req.params.id },
      {
        Alert_Name,
        Object_Class,
        Object_Area,
        Start_Time,
        End_Time,
        Days_Active,
        Holiday_Status,
        Workday_Status,
        Alert_Status,
        Display_Activation,
        Email_Activation,
        Camera_Name,
        Alert_Description,
        No_Object_Status
      }
    );

    await config.updateMany(
      { Camera_Name: { $in: Camera_Name } },
      { $push: { Alert: Alert_Name } }
    );

    res.status(200).json({
      success: true,
      message: "update alert successful",
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
    });
  }
});

router.get(process.env.ALERT_BY_CAMERA_NAME, async (req, res) => {
  try {
    const alerts = await Alert.find({
      Camera_Name: { $in: [req.params.camera_name] },
    });
    res.status(200).json({
      success: true,
      message: "alert list found",
      alerts,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: "unable to found alert",
    });
  }
});

router.put(process.env.DELETE_ALERT, async (req, res) => {
  const _id = req.params.id;
  try {
    const alertInfo = await Alert.findById({
      _id,
    });

    let filterByCName = alertInfo["Camera_Name"].filter((name, index) => {
      return !req.body.Camera_Name.includes(name);
    });

    let updatedRecord = await Alert.findByIdAndUpdate(
      _id,
      {
        Camera_Name: filterByCName,
      },
      { new: true }
    );

     await config.findOneAndUpdate({ Camera_Name: req.body.Camera_Name}, {
        $pull: {
            'Alerts':_id
        } 
      });
      


    if (updatedRecord["Camera_Name"].length === 0) {
      await Alert.findByIdAndDelete(_id);
      return res.status(200).json({
        success: true,
        message: "delete alert successful",
      });
    }

    res.status(200).json({
      success: true,
      message: "delete alert successful",
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
    });
  }
});

router.get(process.env.FIND_CAMERA_BY_ALERT_ID, async (req, res) => {
  const _id = req.params.id;
  try {
    const alertInfo = await Alert.findById({
      _id,
    });
    res.status(200).json({
      success: true,
      message: "successfully found cameras",
      CameraNames: alertInfo["Camera_Name"],
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
    });
  }
});

export default router;
