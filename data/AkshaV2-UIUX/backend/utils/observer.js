//import socketIo from "socket.io";
import path from "path";
import fs from "fs";
import watch from "node-watch";
import config from "../src/models/configSchema";
import mongoose from "mongoose";
import moment from "moment";
import global from "./global.json";
const debug = require("debug")("author");

let client_origin = process.env.CLIENT_ORIGIN;

const observer = (server, app) => {
//  const io = socketIo(server, {
//    cors: {
//      origin: client_origin,
//    },
//  });

  let meta_cameras = [];

  mongoose.connection.on("open", function (ref) {
    mongoose.connection.db
      .listCollections()
      .toArray(async function (err, collectionName) {
        let metaCollection = collectionName.filter((data) => {
          return data["name"].toLocaleLowerCase().includes("meta_");
        });

        for (let i = 0; i < metaCollection.length; i++) {
          const metaSchema = new mongoose.Schema(
            {},
            { collection: metaCollection[i].name, strict: false }
          );

          let metaModel = mongoose.model(metaCollection[i].name, metaSchema);

          let filterMeta = await metaModel
            .find()
            .sort({ Timestamp: -1 })
            .limit(1);
          filterMeta.forEach((data) => {
            meta_cameras.push({
              _id: data.id,
              Timestamp: data.Timestamp,
              Results: data.Results,
              Frame_Anomaly: data.Frame_Anomaly,
              Object_Anomaly: data.Object_Anomaly,
              camera_name: metaCollection[i].name.split("_")[1],
            });
          });
        }
      });
  });

  const fetchMetaCameras = async (socket, app) => {
    // var result = fs.readdirSync(path.join(`${process.cwd()}/Aksha/`));
    const cameraDetail = await config.find();
    let days = fs.readFileSync(`${process.cwd()}/utils/global.json`, "utf-8");
    let { workday } = JSON.parse(days);

    // let filterResult = result.filter((folderName) => {
    //   return folderName.toLocaleLowerCase().includes("camera");
    // });
    let filterResult = cameraDetail.map((folderName) => {
      return folderName.Camera_Name;
    })

    let filterInfo = [];

    filterResult.forEach((cameraName) => {
      let workdayFile = fs.existsSync(
        path.join(
          `${process.cwd()}/Aksha/${cameraName}/spotlight`,
          "workday.jpg"
        )
      );
      let weekdayFile = fs.existsSync(
        path.join(
          `${process.cwd()}/Aksha/${cameraName}/spotlight`,
          "holiday.jpg"
        )
      );

      if (workday === "true") {
        if (workdayFile === true)
          filterInfo.push({
            camera_name: cameraName,
            image:
              `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${cameraName}/spotlight/` +
              "workday.jpg",
          });
      } else if (workday === "false") {
        if (weekdayFile === true)
          filterInfo.push({
            camera_name: cameraName,
            image:
              `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${cameraName}/spotlight/` +
              "holiday.jpg",
          });
      }
    });

    filterResult.forEach((cameraName) => {
      let joinPath = path.join(
        `${process.cwd()}/Aksha/${cameraName}/spotlight`
      );
      let globalPath = path.join(`${process.cwd()}/Aksha/utils/global.json`);
      let workdayFile = fs.existsSync(
        path.join(
          `${process.cwd()}/Aksha/${cameraName}/spotlight`,
          "workday.jpg"
        )
      );
      let weekdayFile = fs.existsSync(
        path.join(
          `${process.cwd()}/Aksha/${cameraName}/spotlight`,
          "holiday.jpg"
        )
      );
      let globalFile = fs.existsSync(path.join(globalPath));

      if (workdayFile == true) {
        watch(joinPath, { recursive: true }, function (evt, name) {
          if (evt === "update")
            socket.emit("meta_cameras", {
              success: true,
              message: "file Updated",
              info: filterInfo,
            });
        });
      } else if (weekdayFile === true)
        watch(joinPath, { recursive: true }, function (evt, name) {
          if (evt === "update")
            socket.emit("meta_cameras", {
              success: true,
              message: "file Updated",
              info: filterInfo,
            });
        });

      if (globalFile == true) {
        fs.watchFile(globalPath, "utf-8", function () {
          if (evt === "update")
            socket.emit("meta_cameras", {
              success: true,
              message: "file Updated",
              info: filterInfo,
            });
        });
      }
    });

    return filterInfo;
  };

  const getCameraName = async (socket, app) => {
    const cameraDetail = await config.find();

    let newCameraDetail = cameraDetail.map((data) => {
      let joinPath = path.join(
        `${process.cwd()}/Aksha/${data.Camera_Name}/live`
      );

      let days = fs.readFileSync(`${process.cwd()}/utils/global.json`, "utf-8");
      let { workday } = JSON.parse(days);
      
      // let host = `${window.location.hostname}`;
      let daysImage =
        workday === "true"
          ? fs.existsSync(path.join(joinPath, "workday.jpg"))
            ? `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${data.Camera_Name}/live/` +
              "workday.jpg"
            : null
          : fs.existsSync(path.join(joinPath, "holiday.jpg"))
          ? `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${data.Camera_Name}/live/` +
            "holiday.jpg"
          : null;

      return {
        _id: data._id,
        Rtsp_Link: data.Rtsp_Link,
        Camera_Name: data.Camera_Name,
        Description: data.Description,
        Feature: data.Feature,
        Priority: data.Priority,
        Status: data.Status,
        Email_Auto_Alert: data.Email_Auto_Alert,
        Display_Auto_Alert: data.Display_Auto_Alert,
        Active:data.Active,
        Skip_Interval: data.Skip_Interval,
        Live: data.Live,
        Surveillance_Status: data.Surveillance_Status,
        PausedImage:
          data.Live === false
            ? fs.existsSync(
                path.join(
                  `${process.cwd()}/Aksha/${data.Camera_Name}/frame`,
                  `${moment(data.PausedTime).format("YYYY-MM-DD HH_mm_ss")}.jpg`
                )
              )
              ? `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/${data.Camera_Name}/frame/` +
                `${moment(data.PausedTime).format("YYYY-MM-DD HH_mm_ss")}.jpg`
              : null
            : null,
        image:
          data.Surveillance_Status === "stop"
            ? fs.existsSync(path.join(`${process.cwd()}/Aksha`, "stop.jpg"))
              ? `${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/` +
                "stop.jpg"
              : null
            : daysImage,
      };
    });

    for (let i = 0; i < newCameraDetail.length; i++) {
      let joinPath = path.join(
        `${process.cwd()}/Aksha/${newCameraDetail[i].Camera_Name}/live`
      );
      let globalPath = path.join(`${process.cwd()}/Aksha/utils/global.json`);

      let workdayFile = fs.existsSync(path.join(joinPath, "workday.jpg"));
      let weekdayFile = fs.existsSync(path.join(joinPath, "holiday.jpg"));
      let globalFile = fs.existsSync(path.join(globalPath));

      if (workdayFile == true)
        // watch(joinPath, { recursive: true }, function (evt, name) {
        //   // debug("%s changed.", name);
        //   // debug(evt);
        //   // debug(evt === "update");
        //   if (evt === "update")
            socket.emit("cameraImages", {
              success: true,
              message: "file Updated",
              info: newCameraDetail,
            });
        // });
      else if (weekdayFile == true)
        // watch(joinPath, { recursive: true }, function (evt, name) {
        //   // debug("%s changed.", name);
        //   // debug(evt);
        //   // debug(evt === "update");
        //   if (evt === "update")
            socket.emit("cameraImages", {
              success: true,
              message: "file Updated",
              info: newCameraDetail,
            });
        // });

      if (globalFile == true) {
        fs.watchFile(globalPath, "utf-8", function () {
          socket.emit("cameraImages", {
            success: true,
            message: "file Updated",
            info: newCameraDetail,
          });
        });
      }
    }

    return newCameraDetail;
  };

  io.on("connection", async (socket) => {
    debug("New client connected");
    let cameraDetail = await getCameraName(socket, app);
    let metaCameraDetail = await fetchMetaCameras(socket, app);

    socket.emit("cameraImages", {
      success: true,
      message: "success",
      info: cameraDetail,
    });

    socket.emit("meta_cameras", {
      success: true,
      message: "success",
      info: metaCameraDetail,
    });

    const changeStream = config.watch();

    changeStream.on("change", function (change) {
      setTimeout(async () => {
        socket.emit("cameraImages", {
          success: true,
          message: "success",
          info: await getCameraName(socket, app),
        });
      }, 500);
    });

    socket.on("disconnect", () => {
      debug("Client disconnected");
      socket.emit("cameraImages", {
        success: false,
        message: "disconnected",
        info: [],
      });

      socket.emit("meta_cameras", {
        success: true,
        message: "disconnected",
        info: [],
      });
    });
  });

  return server;
};

export default observer;
