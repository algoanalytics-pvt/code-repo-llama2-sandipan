import express from "express";
import config from "../models/configSchema";
import fs from "fs";
import path from "path";
const debug = require("debug")("author");

const router = express.Router();

router.get(process.env.CAMERA_NAMES, async (req, res) => {
  try {
    const cameras = await config.find(
      {},
      {
       
      }
    );
    res.status(200).json({
      success: true,
      message: "Fetch All Camera Name Successfully",
      cameras: cameras,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
      cameras: [],
    });
  }
});

router.get(process.env.OBJECT_OF_INTEREST_LABELS, (req, res) => {
  try {
    let joinPath = path.join(`${process.cwd()}/Aksha/labels.txt`);

    let labels = fs.readFileSync(joinPath, "utf-8").split("\n");
    debug(labels)
    res.status(200).json({
      success: true,
      message: "Fetch All Labels Successfully",
      labels: labels,
    });
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error,
      labels: [],
    });
  }
});

router.get(process.env.REFERENCE_IMAGE, (req, res) => {
  try{
    const cam= req.params.camera_name
    const fileData = fs.readFileSync(`${process.cwd()}/Aksha/rtsplinks.json`, 'utf-8');
    // const fileData = fs.readFileSync(`/home/algo5/Aksha_latest_developer/ref-img-Aksha/Aksha-Version-2/Aksha/rtsplinks.json`, 'utf-8');
    const rtspData = JSON.parse(fileData);
    for (const key in rtspData){
      if (rtspData[key]['cam_name']== cam){
        const cam_rtsp_id= rtspData[key]['rtsp_id']

        let imageUrl = `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/Reference_images/${cam_rtsp_id}.jpg`;

    let joinPath = path.join(
          `${process.cwd()}/Aksha/Reference_images/${cam_rtsp_id}.jpg`
    );

    let fileExist = fs.existsSync(path.join(joinPath));

    if (fileExist === true) {
      console.log("Herefdn")
      res.setHeader('Cross-Origin-Resource-Policy', 'same-site');
      return res.status(200).json({
        success: true,
        message: "Fetch Reference Image Successfully",
        image: imageUrl,
      });
    }

    res.status(200).json({
      success: true,
      message: "Fetch Reference Image Successfully",
      image: null,
    });
      }
    }
  } catch (error) {
    res.status(400).json({
      success: false,
      message: error.message,
      image: null,
    });
  }
});

export default router;
