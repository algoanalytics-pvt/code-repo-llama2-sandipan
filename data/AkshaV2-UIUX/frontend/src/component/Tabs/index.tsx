import * as React from "react";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import Box from "@mui/material/Box";
import { TabPanel, TabContext } from "@mui/lab";
import { TabProps } from "./tabs.types";
import { makeStyles } from "@mui/styles";
import { Button } from "@mui/material";
import { useLocation } from "react-router-dom";
import "./tabs.scss";
import MenuItem from "@mui/material/MenuItem";
import FormControl from "@mui/material/FormControl";
import Select, { SelectChangeEvent } from "@mui/material/Select";
import { getDurationTime } from "../../global_store/reducers/investigationReducer";
import { useDispatch } from "react-redux";
import axios from "axios";
// custom styles variable
const useStyles = makeStyles({
  tabBg: {
    background: "white",
  },
  toggleButtonContainer: {
    position: "absolute",
    right: "0",
    border: " 1px solid #0A57EB",
    borderRadius: "17px",
  },
  dropBtn: {
    position: "absolute",
    right: "0",
    top: "-11px",
  },
  toggleClass: {
    background: "#0A57EB!important",
    color: "white!important",
    borderRadius: "16px!important",
    "&:hover": {
      background: "#0A57EB!important",
      color: "white!important",
      borderRadius: "16px!important",
    },
  },
  quantityRoot: {
    "&:hover": {
      backgroundColor: "transparent",
    },
    "&:focus-within": {
      backgroundColor: "transparent",
    },
    "& .MuiOutlinedInput-notchedOutline": {
      border: "0px solid red",
    },
    "&:hover .MuiOutlinedInput-notchedOutline": {
      border: "0px solid #484850",
    },
    "& .Mui-focused .MuiOutlinedInput-notchedOutline": {
      border: "0px solid #484850",
      borderWidth: "0px!important",
    },
  },
});
// main component
function ColorTabs({ tabName, pages }: TabProps) {


  // console.log(`${process.env.REACT_APP_BASE_URL}${process.env.REACT_APP_CHECK_FOR_WORKING_DAY}`, process.env.NODE_ENV);

  // list of state variables
  let location = useLocation();
  // const [value, setValue] = React.useState("one");
  const [value, setValue] = React.useState(() => {
    //use effect takes a function to check prev tabs selected before page refresh if present in memory
    //this function runs only on first mount/initial render i.e only once
    let valued: string = "one";
    if (typeof localStorage["tabValue"] !== "undefined") {
      const itemValue: any = localStorage.getItem('tabValue');
      valued = JSON.parse(itemValue);
    }
    return valued;
  });


  const classes = useStyles();
  // const [toggleDays, setToggleDays] = React.useState(false);


  const [toggleDays, setToggleDays] = React.useState(() => {
    //this function runs only on first mount/initial render i.e only once
    let toggleValue:any = false;
    if (typeof localStorage["WorkHoliday"] !== "undefined") {
      let  currentValue: any = localStorage.getItem('WorkHoliday');
      toggleValue = JSON.parse(currentValue) ===  'Work Day' ? false : true;
    }
    return toggleValue;
  });


  const [age, setAge] = React.useState("1");
  const dispatch = useDispatch();
  // on change tab


  const handleChange = (event: React.SyntheticEvent, newValue: string) => { //change
    setValue(newValue);
    localStorage.setItem('tabValue', JSON.stringify(newValue));
  };


  // on select option
  const selectChange = (event: SelectChangeEvent) => {
    setAge(event.target.value);
    if (event.target.value === "") {
      dispatch(getDurationTime(0));
    } else {
      dispatch(getDurationTime(event.target.value));
    }
  };
  // reminder not gone to participant 
  // @ts-ignore
  const check_for_working_day = (value: any) => {
    localStorage.setItem('WorkHoliday', JSON.stringify(value));

    if (value == 'Work Day') {
      setToggleDays(false)
      axios.get(`${process.env.REACT_APP_BASE_URL}${process.env.REACT_APP_CHECK_FOR_WORKING_DAY}?workday=true`)
        .then((response) => {
        //  console.log('response', response)
        },
          (error) => {
          }
        );
    } else {
      setToggleDays(true)
      axios.get(`${process.env.REACT_APP_BASE_URL}${process.env.REACT_APP_CHECK_FOR_WORKING_DAY}?workday=false`)
        .then((response) => {
         // console.log('response', response)
        },
          (error) => {
            console.log('error', error)
          }
        );
    }
  }
  // html rendered
  return (
    <Box sx={{ width: "100%" }} className="tab-wrapper tab-container-1">
      <TabContext value={value}>
        <div>
          <Tabs
            value={value}
            onChange={handleChange}
            aria-label="secondary tabs example"
            className={`px-4 pt-2 tabBg tabsColor`}
          >
            {tabName.map((tabs, index) => (
              <Tab key={index} value={tabs.value} label={tabs.label} />
            ))}

            {location.pathname === "/monitor" && (
              <div
                className="toggleButtonContainer"
                id="monitor-holiday-buttons"
              >
                <Button
                  // onClick={() => setToggleDays(true)}
                  onClick={() => check_for_working_day("Holiday")}
                  className={toggleDays ? "toggleClass" : ""}
                  style={{ width: "100px" }}
                >
                  Holiday
                </Button>
                <Button
                  // onClick={() => setToggleDays(false)}
                  onClick={() => check_for_working_day("Work Day")}
                  className={toggleDays ? "" : "toggleClass"}
                  style={{ width: "100px" }}
                >
                  Work Day
                </Button>
              </div>
            )}
            {location.pathname === "/investigation" && value === "two" ? (
              <div className="dropBtn">
                <FormControl
                  sx={{ m: 1, minWidth: 120 }}
                  // classes={{
                  //   root: "quantityRoot",
                  // }}
                  className="quantityRoot"
                >
                  <Select
                    value={age}
                    onChange={selectChange}
                    displayEmpty
                    inputProps={{
                      "aria-label": "Without label",
                      underline: {
                        "&&&:before": {
                          border: "none",
                        },
                        "&&:after": {
                          border: "none",
                        },
                      },
                    }}
                  >
                    <MenuItem value="">Duration</MenuItem>
                    <MenuItem value={1} selected={true}>
                      1 hour
                    </MenuItem>
                    <MenuItem value={2}>2 hour</MenuItem>
                    <MenuItem value={3}>3 hour</MenuItem>
                    <MenuItem value={4}>4 hour</MenuItem>
                  </Select>
                </FormControl>
              </div>
            ) : (
              ""
            )}
          </Tabs>
        </div>
        {pages.map((page, index) => (
          <TabPanel key={index} value={page.value}>
            {page.component}
          </TabPanel>
        ))}
      </TabContext>
    </Box>
  );
}

export default React.memo(ColorTabs);