import express from "express";
import notification from "../models/resourceSchema";
const router = express.Router();

router.put(process.env.EMAILNOTIFICATIONUPDATE, async (req, res) => {
  const { Username,
    New_Email,
    Notification_Email } = req.body;
    console.log(req.body)

  if (Notification_Email.length === 0) {
    return res.status(400).json({
      success: false,
      message: "please provide proper data!",
    });
  }
  try {
    const data = await notification.findOne();
    if (data) {
      const { _id } = data;
      await notification.updateOne(
        { id: _id },
        {
          $set: {
            "notification_email": Notification_Email,
            "username": Username,
            "new_email": New_Email
          },
        }
      );
    } else {
      notification.create({
        "notification_email": Notification_Email,
        "username": Username,
        "new_email": New_Email,
      })
    }

    res.status(200).json({
      success: true,
      message: "Email Updated Successfully ",
    });
  } catch (error) {
    console.log(error)
    res.status(400).json({
      success: false,
      message: error,
    });
  }
});

router.get(process.env.EMAILNOTIFICATION, async (req, res) => {
  try {
    const { notification_email } = await notification.findOne();
    res.status(200).json({
      success: true,
      notification_email,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
    });
  }
});

export default router;
