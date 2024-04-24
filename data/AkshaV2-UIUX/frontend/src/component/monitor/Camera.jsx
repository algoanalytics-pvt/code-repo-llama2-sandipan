import React, { useState, useEffect } from "react";
import "./styles/active.scss";

const Camera = ({
  camera,
  surveillance_status,
  liveStatus,
  socket,
  defaultImage,
}) => {
  const [imageUrl, setImageUrl] = useState(defaultImage);
  // console.log({ camera, surveillance_status, defaultImage });
  useEffect(() => {
    console.log("camera img update", {
      camera,
      liveStatus,
    });
    if (liveStatus) {
      socket.on(camera, (data) => {
        console.log(`Update image cam ${camera}`, data);
        setImageUrl(data);
      });
    }
    //     change(imageUrl);

    // Socket off
    return () => {
      socket.off(camera);
    };
  }, [camera, socket, liveStatus]);

  return (
    <img
      crossOrigin="anonymous" // attribute specifies that the img element supports CORS
      src={
        surveillance_status === "stop"
          ? `./assets/img/blackBackImg.jpg`
          : imageUrl
      }
      className={
        surveillance_status === "stop"
          ? "w-100 black-cam-image"
          : "w-100 camera-image"
      } //show black image on camera css om cam container stop
      alt="camera img"
    />
  );
};
export default Camera;
