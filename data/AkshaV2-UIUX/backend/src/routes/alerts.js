import mongoose from "mongoose";
import express from "express";
import { getIsPointInsidePolygon } from "../../utils/getInsidePolygon";
import moment from "moment";
import path from "path";
import fs from "fs";
import config from "../models/configSchema";
const debug = require("debug")("author");
const router = express.Router();

router.post(process.env.MY_ALERT, async (req, res) => {
  const { Start_Time, End_Time, Camera_Name, Start_Date, End_Date } = req.body;
  try {
    if (!Start_Time || !End_Time || !Camera_Name || !Start_Date || !End_Date) {
      return res.status(400).json({
        success: false,
        message: "please provide all detail",
      });
    }

    let findCamera = await config.find({});
    var result = findCamera.map((data) => data.Camera_Name);

    let filterResult = result.filter((folderName) => {
      return folderName.includes(Camera_Name);
    });

    let filterInfo = [];

    filterResult.forEach((cameraName) => {
      var images = fs.readdirSync(
        path.join(`${process.cwd()}/Aksha/${cameraName}/alerts`)
      );
      let filterTimeStamp = images.filter((image) => {
        return image.toLocaleLowerCase().includes("_alert.jpg");
      });
      let removeImageExt = filterTimeStamp.filter((image) => {
        let date = image
          .replace("_alert.jpg", "")
          .replace(":", ":")
          .replace(":", ":");
        let dateValidate = moment(moment(date).format("YYYY-MM-DD HH:mm"))
          .isBetween(
            `${moment(Start_Date).format("YYYY-MM-DD")} ${Start_Time}`,
            `${moment(End_Date).format("YYYY-MM-DD")} ${End_Time}`,
            undefined,
            "[]"
          );
        if (dateValidate == true) {
          var format = "HH:mm:ss";
          let time = moment(moment(date).format("HH:mm"), format),
            start = moment(Start_Time, format),
            end = moment(End_Time, format);

          return time.isBetween(start, end);
        } else return false;
      });
      debug(filterInfo)
      if (removeImageExt.length > 0) {
        filterInfo.push({
          cameraName: cameraName,
          date: removeImageExt,
        });
      }
    });

    let filterAlert = filterInfo.map((data) => {
      if (data.cameraName === Camera_Name)
        return {
          cameraName: data.cameraName,
          images: data.date.map((info) => {
            return (
              `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${data.cameraName}/alerts/` +
              `${info}`
            );
          }),
        };
      else return {};
    });

    res.status(200).json({
      success: true,
      message: "My Alerts are found successfully",
      alert: filterAlert,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message,
      alert: [],
    });
  }
});


router.post(process.env.AUTO_ALERT, async (req, res) => {
  const { camera_name, start_date, end_date, start_time, end_time } = req.body;

  if (!camera_name || !start_date || !end_date || !start_time || !end_time) {
    return res.status(400).json({
      success: false,
      message: "please provide proper data to find alert",
      alert: [],
    });
  }

  try {
    let findCamera = await config.find({});
    var result = findCamera.map((data) => data.Camera_Name);

    let metaAlert = mongoose.connection.db.collection(`meta_${camera_name}`);
    let findMeta = await metaAlert.find().toArray();

    let filterResult = result.filter((folderName) => {
      return folderName.toLocaleLowerCase().includes(camera_name);
    });

    let filterInfo = [];

    filterResult.forEach((cameraName) => {
      var images = fs.readdirSync(
        path.join(`${process.cwd()}/Aksha/${cameraName}/alerts`)
      );
      let filterTimeStamp = images.filter((image) => {
        return image.toLocaleLowerCase().includes("_autoalert.jpg");
      });
      let removeImageExt = filterTimeStamp.filter((image) => {
        let date = image
          .replace("_autoalert.jpg", "")
          .replace("_", ":")
          .replace("_", ":");
        let dateValidate = moment
          (moment(date).format("YYYY-MM-DD HH:mm"))
          .isBetween(
            `${moment(start_date).format("YYYY-MM-DD")} ${start_time}`,
            `${moment(end_date).format("YYYY-MM-DD")} ${end_time}`,
            undefined,
            "[]"
          );
        if (dateValidate == true) {
          var format = "HH:mm:ss";
          let time = moment(moment(date).format("HH:mm"), format),
            start = moment(start_time, format),
            end = moment(end_time, format);

          return time.isBetween(start, end);
        } else return false;
      });

      if (removeImageExt.length > 0) {
        filterInfo.push({
          cameraName: cameraName,
          date: removeImageExt,
        });
      }
    });

    let filterAlert = filterInfo.map((data) => {
      let newDate = data.date.map((infoDate) => {
        let formatDate = infoDate
          .replace("_autoalert.jpg", "")
          .replace("_", ":")
          .replace("_", ":");
        return moment.utc(formatDate).format("YYYY-MM-DD HH:mm:ss");
      });

      if (data.cameraName === camera_name)
        return {
          cameraName: data.cameraName,
          info: findMeta.map((metaData) => {
            if (
              newDate.includes(
                moment.utc(metaData.Timestamp).format("YYYY-MM-DD HH:mm:ss")
              )
            ) {
              return {
                _id: metaData._id,
                UserFeedback: metaData.UserFeedback,
                images:
                  `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${data.cameraName}/alerts/` +
                  `${moment
                    .utc(metaData.Timestamp)
                    .format("YYYY-MM-DD HH:mm:ss")}_autoalert.jpg`,
              };
            }
          }),
        };
      else return {};
    });
    let nullFilter = filterAlert.map((e) => {
      return {
        cameraName: e.cameraName,
        info: e.info.filter((info) => info !== undefined),
      };
    });

    res.status(200).json({
      success: true,
      message: "Auto Alerts are found successfully",
      alert: nullFilter,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message,
      alert: [],
    });
  }
});

router.post(process.env.USERFEEDBACK, async (req, res) => {
  const { cameraName, _id, UserFeedback } = req.body;

  if (!cameraName || !_id || UserFeedback === "") {
    res.status(400).json({
      success: false,
      message: "please provide required field",
    });
  }

  try {
    let metaAlert = mongoose.connection.db.collection(`meta_${cameraName}`);
    await metaAlert.updateOne(
      { _id: mongoose.Types.ObjectId(_id) },
      { $set: { UserFeedback: !UserFeedback } }
    );

    res.status(200).json({
      success: true,
      message: "user feedback submitted successfully",
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message,
    });
  }
});

router.get(process.env.RECENT_ALERT, async (req, res) => {
  try {
    let findCamera = await config.find({});
    var result = findCamera.map((data) => data.Camera_Name);

    let filterResult = result;

    let filterInfo = [];

    filterResult.forEach((cameraName) => {
      var images = fs.readdirSync(
        path.join(`${process.cwd()}/Aksha/${cameraName}/alerts`)
      );
      let filterTimeStamp = images.filter((image) => {
        return image;
      });
      let removeImageExt = filterTimeStamp.filter((image) => {
        let date = image
          .replace("_autoalert.jpg", "")
          .replace("_alert.jpg", "")
          .replace("_", ":")
          .replace("_", ":");

        const customFormat = 'YYYY-MM-DD HH:mm:ss';
        const hourByUser = req.params.hours;
        const time = moment(date, customFormat); //date  ---> 2023-08-02 18:09:00  --> 24 hour format images
        const beforeTime = moment(moment(), customFormat).subtract(Number(hourByUser),  'hours');
        const afterTime = moment(moment(), customFormat);
        const condition = time.isBetween(beforeTime, afterTime, undefined, '[]');

        return condition === true
        // return (
        //   new Date(date) >=
        //   new Date(Date.now() - req.params.hours * 60 * 60 * 1000)
        // );

      });

      if (removeImageExt.length > 0) {
        filterInfo.push({
          cameraName: cameraName,
          date: removeImageExt,
        });
      }
    });

    let filterAlert = filterInfo.map((data) => {
      return {
        cameraName: data.cameraName,
        images: data.date.map((info) => {
          return (
            `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${data.cameraName}/alerts/` +
            `${info}`
          );
        }),
      };
    });

    res.status(200).json({
      success: true,
      message: "Recent Alerts are found successfully",
      alert: filterAlert,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message,
      alert: [],
    });
  }
});

// Define a POST route for the object of interest
router.post(process.env.OBJECT_OF_INTEREST, async (req, res) => {
  // Destructure the request body to get the necessary parameters
  const {
    camera_name,
    start_date,
    end_date,
    start_time,
    end_time,
    object_of_interest,
    area_of_interest,
  } = req.body;

  // Check if all necessary parameters are provided, if not return an error
  if (
    !camera_name ||
    !start_date ||
    !end_date ||
    !start_time ||
    !end_time ||
    !object_of_interest
  ) {
    return res.status(400).json({
      success: false,
      message: "Unable to found alert",
      alert: [],
    });
  }

  try {
    // Get all collections from the MongoDB database
    let collection = await mongoose.connection.db.listCollections().toArray();
    let allAlert = [];
    // Filter collections that have "meta_" in their name
    let metaCollection = collection.filter((data) => {
      return data["name"].toLocaleLowerCase().includes("meta_");
    });

    // Loop through each collection
    for (let i = 0; i < metaCollection.length; i++) {
      // Get the specific collection
      let coll = mongoose.connection.db.collection(metaCollection[i].name);

      // Get all documents from the collection
      let filterMeta = await coll
        .find({ Result: { $not: { $size: 0 } } })
        .toArray();

      let imageUrl = "";
      // Loop through each document
      filterMeta.forEach((data) => {
        // Define the path to the image
        let joinPath = path.join(
          `${process.cwd()}/Aksha/${metaCollection[i].name.split("_")[1]}/`
        );

        // Check if the image file exists
        let fileExist = fs.existsSync(
          path.join(
            `${joinPath}/frame`,
            `${moment.utc(data.Timestamp).format("YYYY-MM-DD HH:mm:ss")}.jpg`
          )
        );

        // If the image file exists, set the imageUrl
        if (fileExist === true) {
          imageUrl =
            `${process.env.PROTOCOL}://${process.env.HOST}:${
              process.env.PORT
            }/${metaCollection[i].name.split("_")[1]}/frame/` +
            `${moment.utc(data.Timestamp).format("YYYY-MM-DD HH:mm:ss")}.jpg`;
        }

        // Push the document data to the allAlert array
        allAlert.push({
          _id: data._id,
          Timestamp: data.Timestamp,
          Results: data.Results.map((result, i) => {
            let x1 = [result.x, result.y];
            let x2 = [result.x + result.w, result.y];
            let x3 = [result.x + result.w, result.y + result.h];
            let x4 = [result.x, result.y + result.h];

            return {
              label: result.label,
              x: x1,
              y: x2,
              w: x3,
              h: x4,
            };
          }),
          Frame_Anomaly: data.Frame_Anomaly,
          Object_Anomaly: data.Object_Anomaly,
          camera_name: metaCollection[i].name.split("_")[1],
          image: imageUrl,
        });
      });
    }
    // Filter the allAlert array based on the time and camera name
    let filterOnTime = allAlert.filter((data) => {
      return (
        moment(moment.utc(data.Timestamp).format("YYYY-MM-DD HH:mm")).isBetween(
          `${moment.utc(start_date).format("YYYY-MM-DD")} ${start_time}`,
          `${moment.utc(end_date).format("YYYY-MM-DD")} ${end_time}`,
          undefined,
          "[]"
        ) && data.camera_name === camera_name
      );
    });

    function isCrowd(data) {
      let count = 0;
      let countarr = [];
      let crowd_thresh = 6
      if (object_of_interest === 'crowd') {
        data.Results.forEach(resultVal => {
          if (resultVal.label === 'person') {
            count += 1;
            if (count >= crowd_thresh) {
              countarr.push(resultVal);
            }
          }
        });
        return countarr;
      } else {
        data.Results.forEach(resultVal => {
          if ( object_of_interest.includes(resultVal.label)){
            countarr.push(resultVal);
          }
        })
        return countarr;
      }
    }
    
    // Filter the alerts based on the object of interest
    let filterAlert = filterOnTime.map((data) => {
      return {
        _id: data._id,
        Timestamp: data.Timestamp,
        Results: isCrowd(data),
        Frame_Anomaly: data.Frame_Anomaly,
        Object_Anomaly: data.Object_Anomaly,
        camera_name: data.camera_name,
        image: data.image,
      };
    });

    // Remove alerts with empty Results
    filterAlert = filterAlert.filter((data) => {
      return data.Results.length > 0;
    });

    // If there is no area of interest, return the filtered alerts
    if (area_of_interest.length === 0) {
      return res.status(200).json({
        success: true,
        message: "Data found successfully",
        alert: filterAlert,
      });
    }

    let newFilterAlert = [];

    // Loop through each alert and filter based on the area of interest
    filterAlert.forEach((data) => {
      let insiderPoints = data.Results.filter((Results) => {
        return ![
          // Check if the points are inside the area of interest
          getIsPointInsidePolygon(Results.x, area_of_interest),
          getIsPointInsidePolygon(Results.y, area_of_interest),
          getIsPointInsidePolygon(Results.w, area_of_interest),
          getIsPointInsidePolygon(Results.h, area_of_interest),
        ].includes(false); // End of array includes check
      }); // End of Results filter

      // If there are points inside the area of interest, add the alert to the newFilterAlert array
      if (insiderPoints.length > 0) {
        newFilterAlert.push({
          _id: data._id,
          Timestamp: data.Timestamp,
          Results: insiderPoints,
          Frame_Anomaly: data.Frame_Anomaly,
          Object_Anomaly: data.Object_Anomaly,
          camera_name: data.camera_name,
          image: data.image,
        }); // End of newFilterAlert push
      } // End of insiderPoints length check
    }); // End of filterAlert forEach

    // Return the new filtered alerts
    res.status(200).json({
      success: true,
      message: "Data found successfully",
      alert: newFilterAlert,
    }); // End of response
  } catch (error) {
    // If there is an error, return the error
    res.status(400).json({
      success: false,
      message: error.message,
      alert: [],
    }); // End of error response
  } // End of try-catch block
}); // End of POST route

export default router;
