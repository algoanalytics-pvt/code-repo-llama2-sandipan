
import React, { useState, useEffect } from 'react';
import ImageModel from "../../../common/imageModel";

const imagesLimit = 4; // since 4 images per page limit

const initialState = { itemsCount: imagesLimit };

const CameraAlertBox = ({ data, indexed }) => {

    const [itemsToShow, setItemsToShow] = useState(initialState);
    const [aIFrames, setAIFrames] = useState([]); //alert data to be shown
    const [open, setOpen] = useState(false);
    const onOpenModal = () => setOpen(true);
    const onCloseModal = () => setOpen(false);
    const [imgUrl, setImgUrl] = useState("");
  const [imageLoader, setImageLoader] = useState(false);

    // console.log('CameraAlertBox', data)

    //show more functionality 
    const showMore = () => {
        if (aIFrames.slice(0, itemsToShow.itemsCount).length === aIFrames.length) { //if Show more(100/100) the resets state to initial  to show as 50
            setItemsToShow({ itemsCount: imagesLimit });
        } else {
            setItemsToShow({ itemsCount: Number(itemsToShow?.itemsCount) + imagesLimit }); //increase max items can be shown by 50
        }
    }
    const openImageLoader = () => {
        setImageLoader(true);
      };

    useEffect(() => {
      
        if (data.images && data.images?.length > 0) {
            //console.log('condtion 1')
            // console.log('CameraAlertBox', data)
            setAIFrames(data.images);
            setItemsToShow(initialState);
        } else {
            //console.log('condtion 2')
            setAIFrames([]);
            setItemsToShow(initialState);
        }
    }, [data])

    return (
        data.images?.length > 0 ? //show nothing if images array empty
            <div className="row mx-0 cam-name-container">

                {indexed !== 0 && <div className="mb-3">
                    <hr className="hr-seperator"   //separate each cameraName with a break , other than first box do for all
                    />
                </div>}

                <div>
                    <h4>{data.cameraName}</h4>
                </div>


                <div className="container-fluid ">
                    <div
                        className="row mt-2 mx-0 images-container">
                        {aIFrames?.length > 0  && //display the array of cam images for current cameraName
                            aIFrames.slice(0, itemsToShow.itemsCount).map((imgg, index) =>
                                <div
                                    className='col-lg-4 col-md-6 col-sm-12 col-xs-12 col-xl-3 col-xl-3 col-xxl-3'
                                    key={index}>
                                <div>
                                    <img
                                        alt="camera img"
                                        crossOrigin="anonymous"
                                        src={imgg}
                                        className="w-100 image-styling"
                                        onClick={() => {
                                            //sets the state for the "ImageModel" to use
                                            setImgUrl(imgg);
                                            openImageLoader();
                                          }}
                                    />
                                </div>
                                </div>
                            )
                        }
                    </div>
                </div>
                {imgUrl && (
        <ImageModel        //only if "imgUrl" is truthy show ImageModel dialog component
          open={imageLoader}
          setOpen={setImageLoader}
          imgUrl={imgUrl}
        />
      )}


                {aIFrames &&  
                 aIFrames.length > 0 &&
                 aIFrames.length > imagesLimit && //hide when Show less(imagesLimit/imagesLimit) i.e 50/50 OR hide when aIFrames.length < imagesLimit 
                <div className="show-more-info">
                  
                         <a className="btn-color" onClick={showMore}>
                            {aIFrames.slice(0, itemsToShow.itemsCount).length < aIFrames.length ? (  //shows increasing each time by 50
                                <span>Show more ({aIFrames.slice(0, itemsToShow.itemsCount).length}/{aIFrames.length})</span>
                            ) : (
                                //resets to show only 50
                                <span>Show less ({aIFrames.slice(0, itemsToShow.itemsCount).length}/{aIFrames.length})</span>
                            )}
                        </a>
                </div>
            }


            </div>
            : null
    );



}

export default CameraAlertBox;