// gives insights and alerts for one date, and reverse-sorts the alerts
import express from "express";
import fs from "fs";
const router = express.Router();

router.use(express.json());

router.post(process.env.INSIGHT_REPORT, (req, res) => {
  const {date} = req.body;
  if (!date) {
    return res.status(400).json({
      success: false,
      message: "date is missing, or in incorrect format",
      report: {},
    });
  }
  try {
    //if json file for the requested date doesnt exist, check the daemon_stat.log file
    if (!fs.existsSync(`${process.cwd()}/Aksha/insight_report/${date}.json`)){

      if (fs.existsSync(`${process.cwd()}/Aksha/daemon_stat.log`)){

        const logData= fs.readFileSync(`${process.cwd()}/Aksha/daemon_stat.log`, 'utf-8');
        if (hasConsecutiveTrueStatus(logData, date)==false) {

          return res.status(400).json({
            success: false,
            message: "Docker daemon was inactive for the day, no data found",
          });

        } else {
          let result = {}; 
          const fileData = fs.readFileSync(`${process.cwd()}/Aksha/insight_report/${date}.json`, 'utf-8');
          const jsonData = JSON.parse(fileData);
            
          if (Object.keys(jsonData)?.length > 0) {
            const sortedAlerts= reverseSortAlerts(jsonData)
            result = sortedAlerts;
          }

          if (Object.keys(result)?.length > 0) {
            return res.status(200).json(result);
          }
          else {
            return res.status(400).json({})
          }
        }
        
      }else{
        return res.status(400).json({
          success: false,
          message: "Daemon status log file not found, check if cron tab was set correctly",
        });
      }
      
    //else get data from the existing json file for the the requested date
    }else{
      let result = {}; 

      //const fileData = fs.readFileSync(`${process.env.PROTOCOL}://${process.env.HOST}:${process.env.PORT}/insight_report/${date.split('-')[0]}/${date.split('-')[1]}/${date}.json`, 'utf8');
        const fileData = fs.readFileSync(`${process.cwd()}/Aksha/insight_report/${date}.json`, 'utf-8');
        const jsonData = JSON.parse(fileData);
        
      if (Object.keys(jsonData)?.length > 0) {
        const sortedAlerts= reverseSortAlerts(jsonData)
        result = sortedAlerts;
      }

      if (Object.keys(result)?.length > 0) {
        return res.status(200).json(result);
      }
      else {
        return res.status(400).json({})
      }
    }
  }catch(ex){
    return res.status(400).json({
      success: false,
      message: "JSON file for the selected date not found.",
      error: ex.message
    })
    
  }
});

// Function to get all dates between start and end date (inclusive)
// function getDates(startDate, endDate) {
//   const dates = [];
//   let currentDate = new Date(startDate);

//   while (currentDate <= new Date(endDate)) {
//     dates.push(currentDate.toISOString().split('T')[0]);
//     currentDate.setDate(currentDate.getDate() + 1);
//   }

//   return dates;
// }
function hasConsecutiveTrueStatus(logData, date) {
  const lines = logData.split('\n');
  let consecutiveTrueCount = 0;
  try{
    for (const line of lines) {
      const parts = line.split(' ');
      if (parts.length >= 3 && parts[0] == date && parts[2] == 'True') {
        consecutiveTrueCount++;
        if (consecutiveTrueCount >= 4) {
          return true;
        }
      } else {
        consecutiveTrueCount = 0;
      }
    }
    return false;
  }catch(error){
    console.log(error)
  }

  
}

const reverseSortAlerts = (jsonData) => {
  const resultObject = {};

  Object.keys(jsonData).forEach((camName) => {
    const camObject = jsonData[camName];
    const alerts = {};

    Object.keys(jsonData[camName].alerts)
      .sort((a, b) => b.localeCompare(a))
      .forEach((time) => {
        alerts[time] = jsonData[camName].alerts[time];
      });

    camObject.alerts = alerts;
    resultObject[camName] = camObject;
  });

  return resultObject;
};

export default router;