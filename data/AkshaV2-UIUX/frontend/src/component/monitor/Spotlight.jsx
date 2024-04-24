//displays a container of images with "autoalert" text (i.e Frame_Anomaly or Object_Anomaly are true) or "camera_name"(i.e Frame_Anomaly or Object_Anomaly are false)
//state changes when socket "meta_cameras" reruns in header.jsx 
//when socket "meta_cameras" reruns the action "getAllSpotLight" reruns which in turn changes "monitor.spotLightCamera" state 


//to be noted
//shares same css file as monitor/Active.jsx
//unable to get data for Spotlight , only getting an empty array from database in socket("meta_cameras") in Header.jsx
//refer to "monitorReducer" redux store

//spotLightCameras array structure for each object in array
//{
//   _id: string;
//   Timestamp: string;
//   Results: [
//     {
//       label: string;
//       x: number;
//       y: number;
//       w: number;
//       h: number;
//       confidence: string;
//     }
//   ];
//   Frame_Anomaly: boolean;
//   Object_Anomaly: boolean;
//   camera_name: string;
//   image: string;
// }


import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import ImageModel from "../common/imageModel";
// import "./active.scss";
import './styles/active.scss'

// main component
const Spotlight = (props) => {

  //redux state for spotLightCameras, action "getAllSpotLight" for state is inside a socket in Header.tsx
  const cameraDetails = useSelector(
    (state) => state.monitor.spotLightCameras.info
  );

  //array of spotLightCameras to be displayed
  const [spotLightCameras, setSpotLightCameras] = useState([]);

  //props to be sent to "ImageModel" component
  const [imageLoader, setImageLoader] = useState(false);
  const [imgUrl, setImgUrl] = useState("");

  //on setUpdateCamera array change boostrap class change
  const [largeClass, setLargeClass] = useState("col-lg-4");
  const [extraLargeClass, setExtraLargeClass] = useState("col-xl-4");
  const [mediumClass, setMediumClass] = useState("col-lg-6");

  // image loader function
  const openImageLoader = () => {
    setImageLoader(true);
  };


  //used to remove scroll but doesnt work
  useEffect(() => {
    var element = document.getElementById("body-tag");
    element.classList.add("hide-scrollbar");
  }, [])

  // reruns on cameraDetails and spotLightCameras state change
  useEffect(() => {
    setSpotLightCameras(cameraDetails);
    setTimeout(() => {
      if (spotLightCameras.length > 0) {
        if (spotLightCameras.length == 1) {
          setLargeClass('col-lg-12');
          setExtraLargeClass('col-xl-12');
          setMediumClass('col-md-12');
        } else if (spotLightCameras.length == 2) {
          setLargeClass('col-lg-6');
          setExtraLargeClass('col-xl-6');
          setMediumClass('col-md-12');
        } else if (spotLightCameras.length == 3) {
          setLargeClass('col-lg-6');
          setExtraLargeClass('col-xl-6');
          setMediumClass('col-md-12');
        } else if (spotLightCameras.length == 4 || spotLightCameras.length == 5) {
          setLargeClass('col-lg-4');
          setExtraLargeClass('col-xl-4');
          setMediumClass('col-md-6');
        } else if (spotLightCameras.length == 6) {
          setLargeClass('col-lg-4');
          setExtraLargeClass('col-xl-4');
          setMediumClass('col-md-6');
        } else if (spotLightCameras.length > 6) {
          setLargeClass('col-lg-3');
          setExtraLargeClass('col-xl-3');
          setMediumClass('col-md-3');
        }
      }
    }, 200);
    return () => {
      setSpotLightCameras([]);
    };
  }, [cameraDetails, spotLightCameras]);

  //component returned by Spotlight.jsx

  //console.log('spotLightCameras--------', spotLightCameras);

  return (
    <div className="">
      <div className="container-fluid">
        <div className="row">
          {spotLightCameras && spotLightCameras.map((info, index) => (
            <div className={`${largeClass} ${extraLargeClass} ${mediumClass} col-sm-12 col-xs-12 videoContainer2 mb-3 px-2`} key={index}>
              <img
                crossOrigin="anonymous"   // attribute specifies that the img element supports CORS
                src={`${info.image}?${new Date().getTime()}`}  
                className="w-100 camera-image"
                alt="camera img"
                onClick={() => {
                  //sets the state for the "ImageModel" to use
                  setImgUrl(`${info.image}?${new Date().getTime()}`);
                  openImageLoader();
                }}
              />
              {info.Frame_Anomaly === true || info.Object_Anomaly === true ? ( //if Object_Anomaly or Frame_Anomaly  true display "Auto Alert" on top left of image
                <div className="auto-alert">Auto Alert</div>
              ) : (
                ""
              )}
              <div className="bottom-content" style={{ opacity: 1 }}>
                <div className="bottomTextContainer">
                  <p className="mb-0 parentText px-2" 
                  style={{ padding: '0 0', background: '#fff' }}   //if Object_Anomaly or Frame_Anomaly  are false  display "camera_name" on bottom left of image
                  >{info.camera_name}</p>
                </div>
              </div>
            </div>
          ))}
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

export default Spotlight;
