import express from "express";
import mongoose from "mongoose";
import config from "../models/configSchema";
import Alert from "../models/myAlertSchema";
import Resource from "../models/resourceSchema";
import path from "path";
import fs from "fs";
import moment from "moment";
const debug = require("debug")("author");
import axios from "axios";
// const { exec } = require('child_process');

const router = express.Router();

router.post(process.env.CAMERA_CREATE, async (req, res) => {
    try {
        const { Camera_Name, Rtsp_Link, Priority, Feature, Description } = req.body;

        const cameras = await config.find().distinct('Rtsp_Link');
        
        let data= fs.readFileSync(`${process.cwd()}/Aksha/app.config`, {encoding:'utf8'});
        data=data.toString()
        let lines= data.split('\n').filter(i => i !== '')
        console.log(lines)
        lines.shift();
        console.log("after shift: ",lines)
        let conf={}
        lines.forEach(line => {
            const [key,value]= line.split('=')
            conf[key.trim()]=value.trim()
        })
        let AppID= conf["APP_ID"]

        // axios request to lambda function
        const response = await axios.post(
            'https://8ygyexnre1.execute-api.ap-south-1.amazonaws.com/dev/get-camera-limit', {
            "AppID": AppID
        });
        const cam_limit = response.data.MaxCamera;

        let isCamLimit;

        if (cameras.length >= cam_limit) {
            isCamLimit = true;
        } else {
            isCamLimit = false;
        }

        if (isCamLimit == false) {
            if (!Camera_Name || !Rtsp_Link || !Priority || !Feature)
                return res.status(400).json({
                    success: false,
                    message: "please fill the missing information",
                });

            try {
                await config.create({
                    Rtsp_Link: Rtsp_Link,
                    Camera_Name: Camera_Name,
                    Description: Description,
                    Feature: Feature,
                    Priority: Priority,
                    Status: "creating",
                    Email_Auto_Alert: true,
                    Display_Auto_Alert: true,
                    Email_Alert: true,
                    Display_Alert: true,
                    Skip_Interval: 10,
                    Alert: [],
                    Active: true,
                });

                res.status(200).json({
                    success: true,
                    isCamLimitExceeded: isCamLimit,
                    message: "camera creation successful",
                });
            } catch (error) {
                res.status(400).json({
                    success: false,
                    message: error,
                });
            }
        } else {
            return res.status(200).json({
                success: true,
                isCamLimitExceeded: isCamLimit,
                message: "Camera limit exceeded",
            });
        }
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message,
        });
    }

});

router.get(process.env.CAMERA_LIST, async (req, res) => {
    debug("req")
    try {
        const cameras = await config.find();
        let filteredCameras = [];
        cameras.forEach((info) => {
            let joinPath = path.join(
                `${process.cwd()}/Aksha/Reference_images/${info.Camera_Name}.jpg`
            );
            let imageUrl = `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/Reference_images/${info.Camera_Name}.jpg`;
            let fileExist = fs.existsSync(joinPath);
            if (fileExist === true) {
                filteredCameras.push({
                    _id: info._id,
                    Rtsp_Link: info.Rtsp_Link,
                    Camera_Name: info.Camera_Name,
                    Description: info.Description,
                    Feature: info.Feature,
                    Priority: info.Priority,
                    Status: info.Status,
                    Email_Auto_Alert: info.Email_Auto_Alert,
                    Display_Auto_Alert: info.Display_Auto_Alert,
                    Email_Alert: info.Email_Alert,
                    Display_Alert: info.Display_Alert,
                    Skip_Interval: info.Skip_Interval,
                    Alert: info.Alert,
                    image: imageUrl,
                    Active: info.Active,
                });
            } else {
                filteredCameras.push({
                    _id: info._id,
                    Rtsp_Link: info.Rtsp_Link,
                    Camera_Name: info.Camera_Name,
                    Description: info.Description,
                    Feature: info.Feature,
                    Priority: info.Priority,
                    Status: info.Status,
                    Email_Auto_Alert: info.Email_Auto_Alert,
                    Display_Auto_Alert: info.Display_Auto_Alert,
                    Email_Alert: info.Email_Alert,
                    Display_Alert: info.Display_Alert,
                    Skip_Interval: info.Skip_Interval,
                    Alert: info.Alert,
                    image: "",
                    Active: info.Active,
                });
            }
        });

        res.status(200).json({
            success: true,
            message: "fetch camera successful",
            cameras: filteredCameras,
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to get cameras",
        });
    }
});

router.post(process.env.CAMERA_LIMIT, async (req, res) => {
    try {
        let cameras = await config.find().distinct('Rtsp_Link');
        // let AppID = req.body.AppID;
       
        let data= fs.readFileSync(`${process.cwd()}/Aksha/app.config`, {encoding:'utf8'});
        data=data.toString()
        let lines= data.split('\n').filter(i => i !== '')
        lines.shift();
        let conf={}
        lines.forEach(line => {
            const [key,value]= line.split('=')
            conf[key.trim()]=value.trim()
        })
        let AppID= conf["APP_ID"]

        // axios request to lambda function
        const response = await axios.post(
            'https://8ygyexnre1.execute-api.ap-south-1.amazonaws.com/dev/get-camera-limit', {
            "AppID": AppID
        });
        console.log(response.data)
        const cam_limit = response.data.MaxCamera;

        let isCamLimit;
        let resMsg;

        if (cameras.length >= cam_limit) {
            isCamLimit = true;
            resMsg = "Camera limit exceeded";
        } else {
            isCamLimit = false;
            resMsg = "Camera limit not exceeded";
        }

        res.status(200).json({
            success: true,
            camLimit: cam_limit,
            isCamLimitExceeded: isCamLimit,
            message: resMsg
        });

    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message,
        });
    }
});

router.put(process.env.UPDATE_CAMERA, async (req, res) => {
    let {
        Rtsp_Link,
        Camera_Name,
        Description,
        Feature,
        Priority,
        Email_Auto_Alert,
        Display_Auto_Alert,
        Email_Alert,
        Display_Alert,
    } = req.body;

    if (
        !Camera_Name ||
        !Rtsp_Link ||
        !Priority ||
        !Feature ||
        !Email_Auto_Alert === "" ||
        !Display_Auto_Alert === ""||
        !Email_Alert === "" ||
        !Display_Alert === ""
    )
        return res.status(400).json({
            success: false,
            message: "please fill the missing information",
        });
    try {
        //find the old camera name (before renaming)
        const camarr = await config.findOne({ "_id": `${req.params.id}` })
        let old_camera_name = camarr["Camera_Name"]
        console.log(old_camera_name, Camera_Name)

        if (Camera_Name == old_camera_name) {
            console.log("inside if block")
            await config.updateOne(
                { _id: req.params.id },
                {
                    $set: {
                        Rtsp_Link: Rtsp_Link,
                        Camera_Name: Camera_Name,
                        Description: Description,
                        Feature: Feature,
                        Priority: Priority,
                        Email_Auto_Alert: Email_Auto_Alert,
                        Display_Auto_Alert: Display_Auto_Alert,
                        Email_Alert: Email_Alert,
                        Display_Alert: Display_Alert,
                        
                    },
                }
            );
            console.log("config collection updated with latest data")

        } else {
            console.log("inside else block")
            //update all my alerts for the camera in Alerts collection with new camera name
            await Alert.updateMany({ Camera_Name: `${old_camera_name}` }, { $set: { Camera_Name: `${Camera_Name}` } })
            console.log("alerts cam name changed")

            // //rename the meta_{camera} collection
            // console.log(old_camera_name, Camera_Name)
            // mongoose.connection.db.collection(`meta_${old_camera_name}`).rename(`meta_${Camera_Name}`);
            // console.log("meta col name changed")

            // rename the camera in config collection
            await config.updateOne(
                { _id: req.params.id },
                {
                    $set: {
                        Rtsp_Link: Rtsp_Link,
                        Camera_Name: Camera_Name,
                        Description: Description,
                        Feature: Feature,
                        Priority: Priority,
                        Email_Auto_Alert: Email_Auto_Alert,
                        Display_Auto_Alert: Display_Auto_Alert,
                        Email_Alert: Email_Alert,
                        Display_Alert: Display_Alert,
                    },
                }
            );
            console.log("config cam name changed")
            //rename the camera folder in Aksha folder on local file system
            // for docker container:

            // fs.rename(`${process.cwd()}/Aksha/${old_camera_name}`, `${process.cwd()}/Aksha/${Camera_Name}`, function (err) {
            //     if (err) console.log('ERROR: ' + err);
            // });
            // console.log("folder name changed")
        }

        // for testing on local system:
        //   fs.rename(`/home/algo5/Aksha_latest_developer/latest-v2/Aksha-Version-2/Aksha/${old_camera_name}`, `/home/algo5/Aksha_latest_developer/latest-v2/Aksha-Version-2/Aksha/${Camera_Name}`, function(err) {
        //     if ( err ) console.log('ERROR: ' + err);
        // });

        res.status(200).json({
            success: true,
            message: "camera update successful"
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to update camera",
            errormsg: error.message
        });
    }
});

router.delete(process.env.DELETE_CAMERA, async (req, res) => {
    const _id = req.params.id;
    try {
        await config.findByIdAndUpdate(_id, { Active: false });
        res.status(200).json({
            success: true,
            message: "camera Inactive successful",
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to Inactive camera",
        });
    }
});

router.get(process.env.ACTIVATE_CAMERA, async (req, res) => {
    const _id = req.params.id;
    try {
        await config.findByIdAndUpdate(_id, { Active: true });
        res.status(200).json({
            success: true,
            message: "camera Activation successful",
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to Activation camera",
        });
    }
});

router.get(process.env.ACTIVE_EMAIL_AUTO_ALERT, async (req, res) => {
    let isAlertActive = JSON.parse(req.query["alert"]);
    try {
        await config.updateMany(
            {
                Email_Auto_Alert: !isAlertActive,
            },
            { $set: { Email_Auto_Alert: isAlertActive } }
        );
        res.status(200).json({
            success: true,
            message: "all email auto alert are active",
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to make all email auto alert active",
        });
    }
});

router.get(process.env.ACTIVE_DISPLAY_AUTO_ALERT, async (req, res) => {
    let isAlertActive = JSON.parse(req.query["alert"]);
    try {
        await config.updateMany(
            {
                Display_Auto_Alert: !isAlertActive,
            },
            {
                $set: {
                    Display_Auto_Alert: isAlertActive,
                },
            }
        );
        res.status(200).json({
            success: true,
            message: "all display auto alert are active",
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to make all display auto alert active",
        });
    }
});

router.get(process.env.ACTIVE_EMAIL_ALERT, async (req, res) => {
    let isAlertActive = JSON.parse(req.query["alert"]);
    try {
        await config.updateMany(
            {
                Email_Alert: !isAlertActive,
            },
            { $set: { Email_Alert: isAlertActive } }
        );
        res.status(200).json({
            success: true,
            message: "all email alert are active",
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to make all email alert active",
        });
    }
});

router.get(process.env.ACTIVE_DISPLAY_ALERT, async (req, res) => {
    let isAlertActive = JSON.parse(req.query["alert"]);
    try {
        await config.updateMany(
            {
                Display_Alert: !isAlertActive,
            },
            {
                $set: {
                    Display_Alert: isAlertActive,
                },
            }
        );
        res.status(200).json({
            success: true,
            message: "all display alert are active",
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to make all display alert active",
        });
    }
});

router.get(process.env.ENABLECAMERA, async (req, res) => {
    let { Live, Camera_Name } = req.query;

    try {
        let liveParse = JSON.parse(Live);
        if (liveParse === false) {
            var result = fs.readdirSync(
                path.join(`${process.cwd()}/Aksha/${Camera_Name}/frame`)
            );
            let filterResult = result.map((fileName) => {
                return moment(
                    fileName.split(".jpg")[0].replace("_", ":").replace("_", ":")
                ).format("YYYY-MM-DD HH:mm:ss");
            });

            await config.updateOne(
                { Camera_Name },
                {
                    Live,
                    PausedTime:
                        filterResult.sort().slice(-1).length > 0
                            ? filterResult.sort().slice(-1)[0]
                            : "null",
                }
            );

            return res.status(200).json({
                success: true,
                message: "success to perform camera operation",
            });
        }

        await config.updateOne({ Camera_Name }, { Live, PausedTime: "null" });

        res.status(200).json({
            success: true,
            message: "success to perform camera operation",
        });
    } catch (error) {
        debug(error);
        res.status(400).json({
            success: false,
            message: "unable to perform camera operation",
        });
    }
});

router.get(process.env.SURVEILLANCESTATUS, async (req, res) => {
    let { Surveillance_Status, Camera_Name } = req.query;

    try {
        await config.updateOne({ Camera_Name }, { Surveillance_Status });

        res.status(200).json({
            success: true,
            message: "success to perform Surveillance operation",
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: "unable to perform Surveillance operation",
        });
    }
});

export default router;