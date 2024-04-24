//used in ObjectOfInterest/index
//creates an image with polygon of area of interest(yellow) and  polygons of Object of Interest(blue)
//A polygon is a closed shape figure that has a minimum of three sides and three vertices 

import React, { useState } from "react";
import ReactDOMServer from "react-dom/server";
//import 'react-responsive-modal/styles.css';
//import { Modal } from 'react-responsive-modal';
import ImageModel from "../../common/imageModel";

const ImageBox = ({ data, aIPolygen }) => {

  const [open, setOpen] = useState(false);
  const onOpenModal = () => setOpen(true);
  const onCloseModal = () => setOpen(false);
  const [imgUrl, setImgUrl] = useState("");
  const [imageLoader, setImageLoader] = useState(false);
  //data: contains the Object of Interest(blue) image and points for polygons of Object of Interest(blue) for each field with their names for each
  //aIPolygen: contains polygon of area of interest(yellow) points

  // Encoding svg 
  function encodeSvg(reactElement) {
    return (
      "data:image/svg+xml," +
      escape(ReactDOMServer.renderToStaticMarkup(reactElement))
    );
  }


  // Get image function
  const getImage = (data) => {


    //-----START-----------------creates an svg with polygon of area of interest(yellow), polygons of Object of Interest(blue) and the Image----------------------
    const image = (
      <svg
        xmlns="http://www.w3.org/2000/svg"       //Required for image/svg+xml files, Optional for inlined <svg>
        width={640}
        height={360}
      >
        <image href={data["base_url"]} width="100%"  //requires href and not src
        />
        {data["Results"].map((Results, index) => {
          return (
            <>
              <polygon          //polygons of Object of Interest(blue)
                key={index}
                points={`${Results.x[0]} ${Results.x[1]},${Results.y[0]} ${Results.y[1]} ,${Results.w[0]} ${Results.w[1]},${Results.h[0]} ${Results.h[1]}`}
                style={{ fill: "transparent", stroke: "blue", strokeWidth: 4 }}
              />
              <text         //name of the Object of Interest(blue)
                text-anchor="middle"
                fontSize={35}
                x={Number(Results.x[0] + 40)}
                y={Number(Results.x[1] - 20)}
                fill="blue"
                style={{ textTransform: 'capitalize' }}
              >{Results.label}</text>
            </>
          )
        })}
        <polygon
          points={aIPolygen}
          style={{ fill: "transparent", stroke: "yellow", strokeWidth: 4 }}            //polygon of area of interest(yellow)
        />
      </svg>
    );

    const openImageLoader = () => {
      setImageLoader(true);
    };
    //---------END------------------------------------


    //encode the svg returned by "const image"  
    return (
      <div>
      <img
      
        src={encodeSvg(image)}
        style={{ width: '100%', borderRadius: 3 }}
        onClick={() => {
          //sets the state for the "ImageModel" to use
          setImgUrl(image);
          openImageLoader();
        }}
      />
      {imgUrl && (
        <ImageModel        //only if "imgUrl" is truthy show ImageModel dialog component
          open={imageLoader}
          setOpen={setImageLoader}
          imgUrl={encodeSvg(image)}
        />
      )}
      </div>
      
    );

  };


  // jsx returned by ImageBox
  return (
    <div>
      <div>{getImage(data)}</div>
    </div>
  );
};

export default ImageBox;
