

//popover snippet taken from mui 5 
//component shows text and on click returns a popover containing list object name labels with different color for active selected 

//to be noted 
//labels.text file needed for it to work else will get error


import * as React from 'react';
import Popover from '@mui/material/Popover';
import Typography from '@mui/material/Typography';
import TruckModel from "./TruckModel";
import '../asterics_styles/asteric.css'

export default function Truck({
  heading,
  text,
  active,
  index,
  setTabStore,
  tabStore,
  setOILable,
  mobile,
}) {
  
//heading, text, active, index, setTabStore, tabStore: this props used to modify  in searchStore state 
// {
//   heading: "Area of Interest",
//   text: "AOI",
//   active: false,
// },
//setOILable: function reference modify state in parent

  const [anchorEl, setAnchorEl] = React.useState(null);
  const [defaultval, setDefaultval] = React.useState("");

  //open modal click event
  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  //close modal click event
  const handleClose = () => {
    setAnchorEl(null);
  };

  //modal custom variables
  const open = Boolean(anchorEl);
  const id = open ? 'simple-popover' : undefined;

  text = typeof text === 'string' ? [text] : text; //[ "person", "car", "helmet" ]

  text = text && text.filter((item, pos) => text.indexOf(item) === pos);  //text.indexOf(item) === pos) if true returns item, 

  return (
    <div id="objectOfInterestCls">
      <div
        className={`inner-content text-center ${active === true && "activeTab"}`}
        key={index}
        onClick={(e) => {
          for (let i = 0; i < tabStore.length; i++) {
            tabStore[i].active = false;
          }

          tabStore[index].active = true;
          //change the active css of the current selected field (i.e active: false)  in tabs

          setTabStore(() => {
            return [...tabStore];
          });

          handleClick(e);
        }}
      >
        {mobile === false && <p><span>{heading.slice(0,-1)}</span><span className='asterics_style'>{heading.charAt(heading.length-1)}</span></p>}
        <p className="text-label mb-0 paragah">
          {text && text.map((ele, idx) => <span >{`${ele}${text.length !== idx + 1 ? ',' : ''}`}</span>  //text.length greater than 1 than add comma after each
          )}
        </p>

      </div>
      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "left",
        }}
        className="model-radius_1"
      >
        <Typography sx={{ p: 1 }}>
          <TruckModel
            setTabStore={setTabStore}
            tabStore={tabStore}
            index={index}
            close={handleClose}
            selectedOption={defaultval}
            setDefaultval={setDefaultval}
            setOILable={setOILable}
          />
        </Typography>
      </Popover>
    </div>
  );
}