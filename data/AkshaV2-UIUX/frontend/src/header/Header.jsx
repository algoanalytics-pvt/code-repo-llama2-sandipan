
//component displays a header with sub-components as follows
//1 -> aksha logo
//2 -> menu dropdown  on small screens and buttons on large screens with a red dot indicator for both
//3 -> setting if logged in
//4 -> user manual modal
//5 -> user profile dropdown

//to be noted
//sockets "meta_cameras" and "cameraImages" currently run every 10 secs cause of new python image every 10 secs in node.js
//ideally node.js should send  a heartbeat event  emit every 10 secs  using pingInterval and pingTimeout in node.js observer.js
//red circle dot was used to show that new camera is added i guess but doesnt work as expected, myabe due to socket rerunning error
//notifications_count is set in active.jsx

//_.xorBy working
// var array1 = [{id:1, busNum: "1234"}, {id:2, busNum:"4567"}],
// array2 = [{id:1, busNum: "2344"}, {id:2, busNum:"1234"}],
// result = _.xorBy(array1, array2, 'busNum');

// ans : result => [{ "id": 2, "busNum": "4567"}, {"id": 1, "busNum": "2344"}]


import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { useLocation, useNavigate } from "react-router-dom";
import socketIOClient from "socket.io-client";
import _ from "lodash";
import { IconButton, Box } from "@mui/material";
import { fetchUser, getAllSpotLight } from "../global_store/reducers/monitorReducer";
import { pages } from "./headerData";
import AppBar from "@mui/material/AppBar";
import logo from "../assets/images/main-logo.png";
import help from "../assets/images/icons/help.png";
import MenuIcon from "@mui/icons-material/Menu";
import UserManual from "./subComponents/UserManual";
import UserProfileDropDown from "./UserProfileDropDown";
import MobileMenu from "./subComponents/MobileMenu";
import Settingss from "./subComponents/Settingss";
import DesktopMenu from "./subComponents/DesktopMenu";
import CustomDropdown from "../component/common/customDropDown";
import './styles/header.scss';
import { getDailyAlertReport } from "../services/alertReportService";
import dayjs from "dayjs";
import { fetchAlertReport, setAlertDate } from "../global_store/reducers/alertReportReducer";



// header component
const Header = () => {
  const dispatch = useDispatch();
  let navigate = useNavigate();
  const location = useLocation();
  const allRoutePathNames = pages.map(item => item.pageUrl); //all route names array uses pages array
  // list of state variables
  const [notificationCount, setNotificationCount] = useState(0);  //stores localstorage notifications_count array length
  const [showNotification, setShowNotification] = useState(false);  //only if notificationCount >0 and depending on location then showNotification is true
  const [selectedModule, setSelectedModule] = useState('');//current selected navigation[index].name
  const [navigation, setNavigation] = useState(pages);//used to change active css
  const [modalopen, setModalopen] = useState(false);//hide/show user manual modal
  const [exitedCameraData, setExitedCameraData] = useState(JSON.parse(window.localStorage?.getItem('notifications_count') || "[]"));
  const [anchorElNav, setAnchorElNav] = React.useState(null);

  const menu = [
    {
      key: '1',
      label: (<a href="#!" onClick={(e) => { e.preventDefault(); setModalopen(true); }}>User Manual</a>),
    },
  ];

  //reruns on selectedModule change
  useEffect(() => {
    if (selectedModule === 'Monitor') {
      localStorage.setItem("notifications_count", JSON.stringify(null));  //reset notifications_count array
      setNotificationCount(0);  // since notifications_count array reset to empty object... reset notificationCount
    }
  }, [selectedModule]);


  //reruns when on REACT_APP_BASE_URL  event "cameraImages" is emitted, needed by monitor.jsx
  useEffect(() => {
    const endpoint = `${process.env.REACT_APP_BASE_URL_PROTOCOL}://${window.location.hostname}:${process.env.REACT_APP_BASE_URL_PORT}`;
    const socket = socketIOClient(endpoint);
    socket.on("cameraImages", (data) => {
      if (window.location.pathname !== '/monitor' && window.location.pathname !== '/' && notificationCount !== 0) { setShowNotification(true); }

      //console.log("====prevState=123=", JSON.parse(window.localStorage?.getItem('notifications_count') || "[]")?.length)
      data.info = [...data.info,
        // { _id: '631af26917acd6eb20e72a2a', Rtsp_Link: 'rtsp://admin:algo1234%23@192.168.2.64:554/Streaming/Channels/701', Camera_Name: 'pandu', Description: 'xyz', Feature: [] },
        //  { _id: '631af26917acd6eb20e72a2a', Rtsp_Link: 'rtsp://admin:algo1234%23@192.168.2.64:554/Streaming/Channels/701', Camera_Name: 'naga', Description: 'xyz', Feature: [] },
        //  { _id: '631af26917acd6eb20e72a2a', Rtsp_Link: 'rtsp://admin:algo1234%23@192.168.2.64:554/Streaming/Channels/701', Camera_Name: 'nagaB', Description: 'xyz', Feature: [] },
        //  { _id: '631af26917acd6eb20e72a2a', Rtsp_Link: 'rtsp://admin:algo1234%23@192.168.2.64:554/Streaming/Channels/701', Camera_Name: 'nagaC', Description: 'xyz', Feature: [] },
        //  { _id: '631af26917acd6eb20e72a2a', Rtsp_Link: 'rtsp://admin:algo1234%23@192.168.2.64:554/Streaming/Channels/701', Camera_Name: 'nagaA', Description: 'xyz', Feature: [] }
      ]

      //so if both arrays(i.e exitedCameraData, data.info,) have object property "Camera_Name"  with same camera name, those  particlar objects will be ignored and empty array will be returned
      //else unique objects in both arrays(i.e exitedCameraData, data.info,) with be returned in a single array "changedObjects"

      // const liveSocket = data.info?.length> 0 ? data.info.map(cam=>cam.Live) : []
     // console.log("=======cameraDetails==data.info==", data.info);

      const changedObjects = _.xorBy(exitedCameraData, data.info, 'Camera_Name');//performs symmetric difference
      setNotificationCount(changedObjects?.length); //used by showNotification for red dot
      dispatch(fetchUser({ info: data.info, message: data.message }));//sends payload whose state is read by monitor.jsx
    });


    // turn socket off 
    // return () => {
    //   socket.off("cameraImages", dispatch(fetchUser({ info: [], message: "" })));
    // };
  }, []); //empty dependency array doesnt matter as it reruns when  event "cameraImages" is emitted 

  // reruns on location.pathname(i.e route) change
  useEffect(() => {
    if (location.pathname && location.pathname === '/monitor') {
      setShowNotification(false); //reset red dot state
    }

    handleRouteChange();
  }, [location]);


  //reruns when on REACT_APP_BASE_URL  event "meta_cameras" is emitted, needed by spotlight.jsx
  useEffect(() => {

    const endpoint = `${process.env.REACT_APP_BASE_URL_PROTOCOL}://${window.location.hostname}:${process.env.REACT_APP_BASE_URL_PORT}`;
    const socket = socketIOClient(endpoint);
    socket.on("meta_cameras", (data) => {
      console.log("==meta cameras==", data);
      dispatch(getAllSpotLight({ info: data.info, message: data.message }));//sends payload whose state is read by spolight.jsx
    });
  }, []); //empty dependency array doesnt matter as it reruns when  event "meta_cameras" is emitted 


  // on open navigation menu click, only for small screens
  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget);
  };

  // on close navigation menu click, only for small screens
  const handleCloseNavMenu = () => {
    setAnchorElNav(null);
  };

  //close the modal and hide from ui
  const handleModalClose = () => {
    setModalopen(false)
  }

  //runs when user  clicks on setting icon image reset active  css and  redirect to settings
  const handleSettingsClick = () => {
    //reset the navigation state to remove active css
    const copyNavigation = navigation.map(page => ({ ...page, active: false }));
    setNavigation((navigation) => copyNavigation);

    localStorage.setItem('tabValue', JSON.stringify("one")); //clear/reset prev page tab selected
    navigate("/cameraDirectory");
  };

  //show css active class for monitor in menu i.e blue box by changing  navigation state on large screens 
  // closing menu and opening respective menu clicked on small screeens
  const handleMenuChange = (page, index, mobileMenu = false) => {
    if (mobileMenu === true) { handleCloseNavMenu(); } // closing menu  on small screens
    //--------works already in location useEffect (i.e function handleRouteChange ) hook so removed prev code----------
    if (page.pageUrl === "/insights") {
      //console.log('435432543543', page.pageUrl)
      handleFetchAlertReport()
    }
    localStorage.setItem('tabValue', JSON.stringify("one")); //clear/reset prev page tab selected
    navigate(page.pageUrl); //goto page like "/monitor"


  }


  const handleFetchAlertReport = async () => {
    const formatedDate = dayjs().subtract(1, 'day').format('YYYY-MM-DD');

    try {
      const { data: allData } = await getDailyAlertReport(formatedDate);
      //console.log('435432543543', formatedDate, dayjs().subtract(1, 'day'),  allData)
      dispatch(fetchAlertReport(allData));
    } catch (error) {
      dispatch(fetchAlertReport({}));
    } finally {
      //written in finally cause of delay in api response time
      // dispatch(setAlertDate(dayjs().subtract(1, 'day')));
      dispatch(setAlertDate(formatedDate));
    }

  }


  //click on  aksha logo takes to route "/monitor"
  const handleLogoClick = () => {
    //--------works already in location useEffect (i.e function handleRouteChange ) hook so removed prev code----------
    localStorage.setItem('tabValue', JSON.stringify("one")); //clear/reset prev page tab selected
    navigate("/monitor");

  }



  //handles change of active css on location.pathname change, persists/resets change on page refresh, 
  const handleRouteChange = () => {
    //currentLocation needed cause monitor has two routes in router (i.e  '/' and '/monitor') and not a redirect(i.e <Navigate to="/monitor" />) instead
    const currentLocation = location.pathname && location.pathname === '/' ?
      '/monitor' : location.pathname ? location.pathname : '';

    if (currentLocation && allRoutePathNames.includes(currentLocation)) {
      const indexx = allRoutePathNames.indexOf(currentLocation);  //index of location pathname, not need to check indexOf == -1 since allRoutePathNames.includes used

      const copyNavigation = navigation.map((page, idx) => indexx === idx ?
        { ...page, active: true } : { ...page, active: false });  //reset all prev css for active, set current index css active to true

      setNavigation((navigation) => copyNavigation);
      setSelectedModule((selectedModule) => copyNavigation[indexx].name); //update selectedModule  (i.e selectedModule="Monitor")
    }
  }

  //html rendered
  return (
    <>
      <AppBar
        position="static"  //fixed to top
        sx={{
          bgcolor: "white",
          boxShadow: "0px 4px 16px 0px #03122E0F",
          position: "fixed",
          zIndex: 999,
          top: 0,
        }}
        className="headerCls"
      >
        <IconButton
          //IconButton only visible on small screen when <Menu collapses 
          //IconButton can take icon like <MenuIcon../> and some text like   <div className..> and creates a button containing them
          size="small"
          aria-label="account of current user"
          aria-controls="menu-appbar"
          aria-haspopup="true"
          onClick={handleOpenNavMenu}
          color="inherit"
          sx={{ flexGrow: 1, display: { xs: "flex", md: "none" } }}
        >
          <MenuIcon style={{ color: "black" }} />
          {(showNotification === true) && (  //show red circle dot on mobile phone sizes only and hide on large screens
            <div className="green-teek d-block d-sm-block d-md-block d-lg-none d-xl-none"></div>
          )}
        </IconButton>

        <img    //aksha logo image
          src={logo}
          alt="aksha logo"
          className="aksha-logo-img"
          onClick={handleLogoClick}
        />
        {(showNotification === true) && ( //show red circle dot show only on large screens and above else hide
          <div className="green-teek d-none d-sm-none d-md-none d-lg-block d-xl-block">
            <></>
          </div>
        )}
        {/* {notificationCount} */}

        <Box sx={{ flexGrow: 1, display: { xs: "flex", md: "none" } }}>
          <MobileMenu  //menu showing Monitor, Investigation, Insights on header, only form small screens
            anchorElNav={anchorElNav}
            onCloseNavMenu={handleCloseNavMenu}
            navigation={navigation}
            onItemSelect={handleMenuChange}
          />
        </Box>

        <Box sx={{ flexGrow: 1, display: { xs: "none", md: "flex" }, justifyContent: "center" }}>
          <DesktopMenu              //on medium screens and above instead of dropdown show buttons 
            navigation={navigation}
            onMenuChange={handleMenuChange}
          />
        </Box>

        <Box sx={{ flexGrow: 0, display: "flex", alignItems: "center" }}>

          <Settingss onSettingsClick={handleSettingsClick} />

          <CustomDropdown //shows user manual
            items={menu}
          >
            <img
              src={help}   //icon image  for user manual
              alt="help"
              className="mx-2 user-manual-img"
            />
          </CustomDropdown>

        </Box>

        {/* user profile options */}
        <UserProfileDropDown />

      </AppBar>

      <UserManual
        value={modalopen}
        onModalClose={handleModalClose}
      />

    </>
  );
};


export default Header;
