
//display alert report for last 10 days excluding today
//when click on insight button gets report for yesterday

// "10111": {
//     "object_detection_alerts": {},
//     "total_alerts_generated": 0,
//     "most_active_hour_for_each_object": {},
//     "peak_alert_time_hour": null,
//     "alerts": {}
// },


import { searchTabs } from "./searchStore";
import './styles/alertReport.scss';
import { useState, useEffect, useCallback } from 'react';
import SearchIcon from "@mui/icons-material/Search";
import dayjs from 'dayjs'; //formats time like moment.js
import { Modal, Spin, message } from "antd";
import NotFound from "../../common/notFound";
import useRemoveScroll from "../../../hooks/useRemoveScroll";
import CustomTable from "./CustomTable/CustomTable";
import DoughnutChart from "./Charts/DoughnutChart";
import HorizontalBarChart from "./Charts/HorizontalBarChart";
import CustomDateSelector from "./CustomDateSelector";
import { useDispatch, useSelector } from "react-redux";
import { fetchAlertReport, setAlertDate } from "../../../global_store/reducers/alertReportReducer";
import { getDailyAlertReport } from "../../../services/alertReportService";
import Messagebox from "../../common/messagebox/Messagebox";
import { Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle, Button, CircularProgress, Box } from '@mui/material'; 


//'./assets/img/alert.png'
// total_alerts_generated: pie chart
// object_detection_alerts: horizontal bar chart


const AlertReport = () => {

    const [tabStore, setTabStore] = useState(searchTabs); //tabs array to be shown in ui
    const [loader, setLoader] = useState(false); //antd spinner state
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [modalImage, setModalImage] = useState(null);
    const [open, setOpen] = useState(false);
    const [message, setMessage] = useState("");
    const handleClose = () => {
        setOpen(false);
      };

    const dispatch = useDispatch();

    let reportDataaa = useSelector(
        (state) => state.alertReport.reportData
    );

    // const [value, setValue] = React.useState(dayjs('2022-04-07')); //mui snippet allowed state
    let dated = useSelector(   //date saved in redux due to inconsistency between tabs, also when shift across tabs cannot clear redux reportDataaa as it is needed  for when lciked on insight button 
        (state) => state.alertReport.alertDate
    );
    // console.log('dateddated', dated);

    const [dependencyArr, setDependencyArr] = useState([]);  //used to remove scroll, scrolls up when no data there

    //runs on reportDataaa change
    useEffect(() => {
        const dependencyArray = Object.keys(reportDataaa || {} ).length > 0 ? new Array(1) : [];
        setDependencyArr(dependencyArray)
    }, [reportDataaa]);


    //runs on first render
    useEffect(() => {
        populateDropDownOnMount();   //set only tabstore default values

        //used to remove scroll from  screen "on mount"  but doesnt work
        var element = document.getElementById("body-tag");
        element.classList.add("hide-scrollbar");

    }, []);


    const handleChangeActiveCss = (index) => {
        const tabStoreCopy = tabStore.map((tab) => ({ ...tab, active: false }));     //remove active css from all objects/fields in tabs array
        tabStoreCopy[index].active = true; //change the active css of the current selected field (i.e active: false) in tabs array
        setTabStore((tabStore) => tabStoreCopy);
        //console.log('handleChangeActiveCss ---  tabStoreCopy', tabStoreCopy);
    };

    const populateDropDownOnMount = () => {

        try {
            setLoader(true);
            const formatedDate = dayjs(dated).format('DD/MM/YY');
            const tabStoreCopy = tabStore.map((tab, index) => ({ ...tab, text: `${formatedDate}` }));
            setTabStore((tabStore) => tabStoreCopy); // setting default values for dates on first render

        } catch (ex) {
            //console.log('error', ex);
        } finally {
            setLoader(false);
        }

    };

    const handleShowModal = (imagee) => {
        setIsModalOpen(true);
        setModalImage(imagee);
    };

    const handleOk = () => {
        setIsModalOpen(false);
        setModalImage(null); //reset modal image
    };

    const handleCancel = () => {
        setIsModalOpen(false);
        setModalImage(null); //reset modal image
    };

    const handleDateChanged = (datee, index) => {
        const formatedDate = dayjs(datee).format('YYYY-MM-DD');
        dispatch(setAlertDate(formatedDate));
        //so if user changes date and doesnt click search that prev  report data there in redux (if user changes sub-tabs)
        //so for that on date change i clear report data in redux
        dispatch(fetchAlertReport({}));
    };


    // console.log('modalImage', modalImage)

    const getReportData = async () => {

        dispatch(fetchAlertReport({}));  //reset
        const formatedDate = dayjs(dated).format('YYYY-MM-DD');

        //validation rules with respective toast message
        if (!formatedDate) {
            //message.warning("Please select date.");
            setMessage("Please select date.")
            setOpen(true);
            return;
        }

        setLoader(true);

        try {
            const { data: allData } = await getDailyAlertReport(formatedDate);
            dispatch(fetchAlertReport(allData));
        } catch (error) {
            dispatch(fetchAlertReport({}));
            //message.warning("No Alerts Found.");
            setMessage("No Alerts Found.")
            setOpen(true);
        } finally {
            setLoader(false);
        }

    };

    //scroll to top by default if no data there, disable scroll for emprt object 
    useRemoveScroll(dependencyArr);//if empty dependency Array sent removes scroll else does not remove scroll

    //used cause tabstore used to display date on searchbar has its own state
    const handleTabStoreonDateChange = useCallback(() => {
        const index = 0
        //console.log('handleDateChanged',)
        const tabStoreCopy = [...tabStore];
        const obj = { ...tabStoreCopy[index] };
        const formatedDate = dayjs(dated).format('DD/MM/YY');
        obj.text = `${formatedDate}`
        tabStoreCopy[index] = obj;
        setTabStore((tabStore) => tabStoreCopy);
    }, [dated])


    //re-reuns on date change
    useEffect(() => {
        handleTabStoreonDateChange()
    }, [dated, handleTabStoreonDateChange]);

    return (

        <>
            {/* <Modal  //modal to show alert image
                title=""
                open={isModalOpen}
                onOk={handleOk}
                onCancel={handleCancel}
                footer={false}
                style={{ maxHeight: 450 }}
            > */}
             <Dialog
                open={isModalOpen}
                onClose={handleCancel}
                maxWidth="md" // Adjust the width as needed
                fullWidth // Set to true to make the dialog full width
                >
                <DialogTitle></DialogTitle>
                <DialogContent>
                <div className="report-alert-modal-container">
                    <div className="add-margin"></div>
                    {modalImage &&
                        <img
                            alt="alert img"
                            crossOrigin="anonymous" // attribute specifies that the img element supports CORS
                            src={modalImage}
                            className="report-alert-camera-img"
                        />}
                </div>
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleOk} color="primary">
                    OK
                    </Button>
                    <Button onClick={handleCancel} color="primary">
                    Cancel
                    </Button>
                </DialogActions>
                </Dialog>
            
            <div>

            </div>
            <div className="alert-report autoalert-search-bar">
            <Messagebox
                open={open}
                handleClose={handleClose}
                message={message}
            />
                <div className="desktop-blue-container">

                    <div className="items-container">
                        {tabStore.map((tab, index) =>
                            //tab design for desktop, custom code and css used 
                            tab.heading === "Date*" ?
                                <div className="each-item"
                                    key={'desktop-search-DatePickerPopover'}
                                >

                                    <CustomDateSelector
                                        value={dayjs(dated)}
                                        onChange={handleDateChanged}
                                        heading={tab.heading}
                                        text={tab.text}
                                        active={tab.active}
                                        index={index}
                                        onChangeActiveCss={handleChangeActiveCss}
                                        mobile={false}
                                    />
                                </div>
                                :
                                null
                        )}
                    </div>

                    <div className="search-Icon-item"
                        onClick={() => getReportData()}
                    >
                        <SearchIcon
                            style={{ fontSize: '2rem' }}
                        //onClick={() => getReportData()}
                        />
                    </div>

                </div>


                <div className='mobile-search'>

                    {tabStore.map((tab, index) =>
                        tab.heading === "Date*" ?
                            <div className="single_item"
                                key={'mobile-search-DatePickerPopover'}
                            >
                                <label>Date<span>*</span></label>
                                <CustomDateSelector
                                    value={dayjs(dated)}  //dayjs used since mui snippet shows it needs time in that format
                                    onChange={handleDateChanged}
                                    heading={tab.heading}
                                    text={tab.text}
                                    active={tab.active}
                                    index={index}
                                    onChangeActiveCss={handleChangeActiveCss}
                                    mobile={true}
                                />
                            </div>
                            :
                            null

                    )}
                    <button
                        className="search-button"
                        onClick={() => getReportData()}
                    >
                        <i className='bx bx-search'></i>
                        Search
                    </button>
                </div>

                {/* <Spin spinning={loader}> */}
                {loader ? (
                <Box
                    position="absolute"
                    top="50%" 
                    left="50%" 
                    transform="translate(-50%, -50%)" 
                >
                <CircularProgress />
                    </Box>
                ) : (
                    <>
                    {Object.keys(reportDataaa || {} )?.length > 0 ?  //check if data present , check if cam names present in data

                        <div className="row mt-3 mx-auto mt-5">

                            <div className="col-lg-8 ">
                                <CustomTable data={reportDataaa} showModal={handleShowModal} />
                            </div>

                            <div className="col-lg-4 ">

                                <div className="row mb-5">
                                    <div className="col-12">
                                        <div className="graph-container">
                                            <DoughnutChart data={reportDataaa} />
                                        </div>
                                    </div>
                                </div>

                                <HorizontalBarChart data={reportDataaa} />

                            </div>
                        </div> :
                        <div className="my_alert_not_found my-5">
                            <NotFound />
                        </div>
                    }
                    </>
                )}
                {/* </Spin> */}

            </div>

        </>
    );
}

export default AlertReport;