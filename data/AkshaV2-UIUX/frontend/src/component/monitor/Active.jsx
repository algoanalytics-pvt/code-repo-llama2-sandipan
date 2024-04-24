//this component is used to create a container of cams using bootsrap where only cam.Active === true cams are shown
//clicking on cam image shows dialog with current image frame you can  use
//you can pause and play image
//change in no of cams changes boostrap class
//currently only in linux cam images updating after some secs, ideally images update only on pause and play
//this component state  changes when  "fetchUser" actions in monitorReducer updates cameraDetails state
//"fetchUser" actions in monitorReducer updates only on socket("cameraImages") run  in Header.jsx useEffect

//to be noted
//notifications_count has a slice in redux state as state.monitor.notificationsCount but this redux state is never used anywhere
//found pause play logic not working properly, maybe cause in linux  images updating after some secs causes state to keep changing
//notifications_count localstorage is changed in Header.jsx
//shares css file with monitor/Spotlight.jsx

//updateCamera  array structure for each object in array
//{
//   _id: string;
//   rtsp_link: string;
//   Camera_Name: string;
//   skip_interval: number;
//   status: boolean;
//   image: string;
// }

///playing shows pause icon
///paused shows play icon

import { useEffect, useState } from "react";
import { Button } from "@mui/material";
import { message } from "antd";
import { useSelector } from "react-redux";
import * as socketIO from "socket.io-client";
import Camera from "./Camera";
import axios from "axios";
import Menu from "../video_menu";
import ImageModel from "../common/imageModel";
// import "./active.scss";
import onPauseIcon from "../../assets/images/icons/pause.png";
import onPlayIcon from "../../assets/images/icons/play.png";
import "./styles/active.scss";
import Messagebox from "../common/messagebox/Messagebox";

const socket = socketIO.connect("http://localhost:5000");

// main component
const Active = (props) => {
  //redux state for cameraDetails, action for state is in socket("cameraImages") in Header.tsx
  const cameraDetails = useSelector(
    (state) => state.monitor.cameraDetails.info
  );
  // const notificationsCountData = useSelector(
  //   (state) => state.monitor.notificationsCount
  // );

  //const [oldCmeraList, setOldCameraList] = useState(notificationsCountData);

  //cams to be displayed on screen
  const [updateCamera, setUpdateCamera] = useState([]);

  //props to be sent to "ImageModel" component
  const [imageLoader, setImageLoader] = useState(false);
  const [imgUrl, setImgUrl] = useState("");

  //arr of stopped cams e.g:['camera_name_1', 'camera_name_2',]
  const [stoppedCameras, setStoppedCameras] = useState([]); //stoppedCameras is changed only on pause and play

  //on setUpdateCamera array change boostrap class change
  const [largeClass, setLargeClass] = useState("col-lg-4");
  const [extraLargeClass, setExtraLargeClass] = useState("col-xl-4");
  const [mediumClass, setMediumClass] = useState("col-md-6");
  const [open, setOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [warning, setWarning] = useState(true);
  const [showFunctionDropdown, setShowFunctionDropdown] = useState(false);

  const handleClose = () => {
    setOpen(false);
  };
  //reruns on cameraDetails  state change in redux
  useEffect(() => {
    //if notifications_count array is empty add the current cameraDetails redux state  as notifications_count array
    if (
      (window.localStorage?.getItem("notifications_count") &&
        JSON.parse(window.localStorage?.getItem("notifications_count") || "[]")
          ?.length === 0) ||
      window.localStorage?.getItem("notifications_count") === null ||
      window.localStorage?.getItem("notifications_count") === "null"
    ) {
      localStorage.setItem(
        "notifications_count",
        JSON.stringify(cameraDetails)
      );
    }

    //when cam is deleted then its Active is changed from true to false in mongoDB
    //if only cam.Active === true then only display on "/monitor"
    const allActiveCameras = cameraDetails.filter((cam) => cam.Active === true);
    setUpdateCamera(allActiveCameras);

    return () => {
      setUpdateCamera([]);
    };
  }, [cameraDetails]);

  //used to remove scroll from monitor screen "on mount"  but doesnt work
  useEffect(() => {
    var element = document.getElementById("body-tag");
    element.classList.add("hide-scrollbar");
  }, []);

  //reruns on updateCamera state change
  useEffect(() => {
    //whn updateCamera state changes change boostrap for largeClass, extraLargeClass, mediumClass
    setTimeout(() => {
      if (updateCamera.length > 0) {
        if (updateCamera.length == 1) {
          setLargeClass("col-lg-12");
          setExtraLargeClass("col-xl-12");
          setMediumClass("col-md-12");
        } else if (updateCamera.length == 2) {
          setLargeClass("col-lg-6");
          setExtraLargeClass("col-xl-6");
          setMediumClass("col-md-12");
        } else if (updateCamera.length == 3) {
          setLargeClass("col-lg-6");
          setExtraLargeClass("col-xl-6");
          setMediumClass("col-md-12");
        } else if (updateCamera.length == 4 || updateCamera.length == 5) {
          setLargeClass("col-lg-4");
          setExtraLargeClass("col-xl-4");
          setMediumClass("col-md-6");
        } else if (updateCamera.length == 6) {
          setLargeClass("col-lg-4");
          setExtraLargeClass("col-xl-4");
          setMediumClass("col-md-6");
        } else if (updateCamera.length > 6) {
          setLargeClass("col-lg-3");
          setExtraLargeClass("col-xl-3");
          setMediumClass("col-md-6");
        }
      }
    }, 200);
    return () => {};
  }, [updateCamera]);

  // play function //takes two arguments i.e param : boolen , Camera_Name : string
  //called when info.Live == true
  const play = (param, Camera_Name) => {
    //param:current "Live state" of "Camera_Name" in mongoDB
    let react_app_base_url = `${process.env.REACT_APP_BASE_URL_PROTOCOL}://${window.location.hostname}:${process.env.REACT_APP_BASE_URL_PORT}`;
    let url = `${react_app_base_url}/api/enableCamera?Live=${param}&Camera_Name=${Camera_Name}`; //toggle   "Live state" of "Camera_Name" in mongoDB

    axios
      .get(url)
      .then(function (response) {
        let arr = stoppedCameras.length > 0 ? stoppedCameras : [];
        arr = arr.filter((cam) => cam !== Camera_Name); //was prevoiusly arr.pop(Camera_Name) but removed it as pop doesnt take an argument

        setStoppedCameras(arr); //removes previously added  cam from  stoppedCameras
        setMessage('Camera "' + Camera_Name + '" is resumed successfully.');
        setWarning(false);
        setOpen(true);
        // Update Live attribute of camera ith Camera_Name
        const index = updateCamera.findIndex(
          (cam) => cam.Camera_Name === Camera_Name
        );
        const updated = [...updateCamera];
        if (index !== -1) {
          updated[index].Live = param;
        }
        setUpdateCamera(updated);
      })
      .catch(function (error) {});
  };

  // pause function  //takes two arguments i.e param : boolen , Camera_Name : string
  //called when info.Live == false
  const pause = (param, Camera_Name) => {
    let url = `${
      process.env.REACT_APP_BASE_URL
    }/api/enableCamera?Live=${param}&Camera_Name=${Camera_Name}`; //toggle   "Live state" of "Camera_Name" in mongoDB
    axios
      .get(url)
      .then(function (response) {
        let arr = stoppedCameras.length > 0 ? stoppedCameras : [];
        arr.push(Camera_Name); //adds  Camera_Name to  stoppedCameras
        setStoppedCameras(arr);
        setMessage('Camera "' + Camera_Name + '" is paused successfully.');
        setWarning(false);
        setOpen(true);
        // Update Live attribute of camera ith Camera_Name
        const index = updateCamera.findIndex(
          (cam) => cam.Camera_Name === Camera_Name
        );
        const updated = [...updateCamera];
        if (index !== -1) {
          updated[index].Live = param;
        }
        setUpdateCamera(updated);
      })
      .catch(function (error) {});
  };

  // image loader
  const openImageLoader = () => {
    setImageLoader(true);
  };

  //show cam menu without hover on container stop
  const getContainerStopCamMenu = (info) => {
    const prevStyle = stoppedCameras.includes(info.Camera_Name)
      ? "flex-end2"
      : "flex-end"; //flex-end2 -- opacity 1 , flex-end -- opacity 0
    if (!stoppedCameras.includes(info.Camera_Name)) {
      //setShowFunctionDropdown(false);
    }
    return info.Surveillance_Status === "stop" ? "flex-end2" : prevStyle;
  };

  //show cam name  without hover on container stop
  const getContainerStopCamName = (info) => {
    const prevStyle = stoppedCameras.includes(info.Camera_Name)
      ? "bottom-content2"
      : "bottom-content"; //bottom-content2-- opacity 1 , bottom-content -- opacity 0
    return info.Surveillance_Status === "stop" ? "bottom-content2" : prevStyle;
  };

  const checkmouseout = () => {
    setShowFunctionDropdown(false);
  };

  function handleCameraImage(img_from_socket) {
    setImgUrl(img_from_socket);
  }

  // component returned for Active.jsx
  return (
    <div>
      <Messagebox
        open={open}
        handleClose={handleClose}
        message={message}
        warning={warning}
      />
      <div className="container-fluid">
        <div className="row">
          {updateCamera.map((info, index) => {
            if (info.Active == true) {
              //show only active cameras
              return (
                <div
                  id={info.Camera_Name}
                  className={`${largeClass} ${extraLargeClass} ${mediumClass} col-sm-12 col-xs-12 videoContainer2 mb-3 px-2`}
                  key={index}
                  onMouseLeave={() => checkmouseout()}
                >
                  <Camera
                    key={info.Camera_Name}
                    camera={info.Camera_Name}
                    surveillance_status={info.Surveillance_Status}
                    liveStatus={info.Live}
                    socket={socket}
                    defaultImage={`${info.image}?${new Date().getTime()}`}
                  />

                  <div className="flex-end">
                    <Menu
                      info={info} //menu has options start, stop camera etc, takes "info" object as prop
                      setMessage={setMessage}
                      setOpen={setOpen}
                      setShowFunctionDropdown={setShowFunctionDropdown}
                      showFunctionDropdown={showFunctionDropdown}
                    />
                  </div>
                  <div className={getContainerStopCamName(info)}>
                    <div className="bottomTextContainer">
                      <p
                        className="mb-0 parentText px-2" //camera name shown at bottom of each image, doesn't work as expected for color change on change of stoppedCameras state
                        style={{ padding: "0 0", background: "#fff" }}
                      >
                        {info.Camera_Name}
                      </p>
                    </div>
                  </div>

                  <div
                    className={
                      stoppedCameras.includes(info.Camera_Name)
                        ? "middle2"
                        : "middle1"
                    }
                  >
                    {info.Live == true ? ( //when pause or play is clicked info.Live value toggles, shows different button image for pause or play
                      <Button onClick={() => pause(false, info.Camera_Name)}>
                        <img src={onPlayIcon} alt="pause video" />
                      </Button>
                    ) : (
                      <Button onClick={() => play(true, info.Camera_Name)}>
                        <img src={onPauseIcon} alt="play video" />
                      </Button>
                    )}
                  </div>
                </div>
              );
            }
          })}
        </div>
      </div>

      {imgUrl && (
        <ImageModel //only if "imgUrl" is truthy show ImageModel dialog component
          open={imageLoader}
          setOpen={setImageLoader}
          imgUrl={imgUrl}
        />
      )}
    </div>
  );
};

export default Active;
